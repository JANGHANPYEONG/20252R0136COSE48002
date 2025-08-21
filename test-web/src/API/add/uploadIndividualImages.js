import JSZip from 'jszip';
import { apiIP } from '../../config';

/**
 * 파일명을 SHA-256 해시로 변환하는 함수
 * @param {string} originalFileName - 원본 파일명 (예: "140119100857_s1_430nm.png")
 * @returns {Promise<string>} - 해시된 파일명 (예: "abc123def_430nm.jpg")
 */
const hashFileName = async (originalFileName) => {
  // 파장 정보 추출 (430nm, 540nm, rgb 등)
  const wavelengthMatch = originalFileName.match(/(\d{3,4}nm|rgb)/i);
  const wavelength = wavelengthMatch ? wavelengthMatch[1].toLowerCase() : '';
  
  // 원본 파일명을 해시화
  const encoder = new TextEncoder();
  const data = encoder.encode(originalFileName);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  
  // 해시의 첫 8자리 사용하여 새로운 파일명 생성
  const shortHash = hashHex.substring(0, 8);
  const extension = 'jpg'; // BE에서 JPEG 형식을 기본으로 사용
  
  if (wavelength) {
    return `${shortHash}_${wavelength}.${extension}`;
  } else {
    return `${shortHash}.${extension}`;
  }
};

/**
 * BE에서 벌크 presigned URL을 요청하는 함수
 * @param {Array} fileList - 파일 목록 [{filename, content_type}, ...]
 * @returns {Promise<Object>} - 벌크 presigned URL 정보
 */
const getBulkPresignedUrls = async (fileList) => {
  try {
    const response = await fetch(`http://${apiIP}/data-upload/bulk-presigned-url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        files: fileList
      })
    });
    
    if (!response.ok) {
      throw new Error(`벌크 Presigned URL 요청 실패: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
    
  } catch (error) {
    console.error('벌크 Presigned URL 요청 오류:', error);
    throw error;
  }
};

/**
 * Presigned URL을 사용하여 S3에 이미지를 업로드하는 함수
 * @param {string} uploadUrl - S3 presigned upload URL
 * @param {Blob} imageBlob - 이미지 파일 Blob
 * @param {string} fileName - 파일명
 * @returns {Promise<Object>} - 업로드 결과
 */
const uploadToS3WithPresigned = async (uploadUrl, imageBlob, fileName) => {
  try {
    // S3에 직접 PUT 요청으로 업로드
    const uploadResponse = await fetch(uploadUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'image/jpeg'
      },
      body: imageBlob
    });
    
    if (!uploadResponse.ok) {
      const errorText = await uploadResponse.text();
      throw new Error(`S3 업로드 실패: ${uploadResponse.status} ${errorText}`);
    }
    
    return {
      success: true,
      filename: fileName
    };
    
  } catch (error) {
    console.error('S3 업로드 오류:', error);
    throw error;
  }
};

/**
 * PNG를 JPEG로 변환하는 함수
 * @param {Blob} pngBlob - PNG 파일 Blob
 * @param {number} quality - JPEG 품질 (0.1-1.0)
 * @returns {Promise<Blob>} - JPEG Blob
 */
const convertPngToJpeg = async (pngBlob, quality = 0.9) => {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      
      // 흰색 배경 추가 (PNG 투명도 처리)
      ctx.fillStyle = 'white';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      // 이미지 그리기
      ctx.drawImage(img, 0, 0);
      
      // JPEG Blob으로 변환
      canvas.toBlob(resolve, 'image/jpeg', quality);
    };
    
    img.onerror = reject;
    img.src = URL.createObjectURL(pngBlob);
  });
};

/**
 * ZIP 파일에서 개별 이미지를 추출하고 해싱하여 S3에 업로드하는 함수
 * @param {File} zipFile - 이미지가 포함된 ZIP 파일
 * @param {string} traceNum - 이력번호
 * @param {Function} progressCallback - 진행상황 콜백 함수 (선택사항)
 * @returns {Promise<Object>} - 업로드 결과
 */
export const uploadIndividualImages = async (zipFile, traceNum, progressCallback = null) => {
  try {
    console.log('ZIP 파일 압축 해제 시작...');
    
    // ZIP 파일 압축 해제
    const zip = new JSZip();
    const zipContent = await zip.loadAsync(zipFile);
    
    // 이미지 파일만 필터링 (jpg, jpeg, png)
    const imageFiles = Object.keys(zipContent.files)
      .filter(fileName => {
        const ext = fileName.split('.').pop().toLowerCase();
        return ['jpg', 'jpeg', 'png'].includes(ext) && !zipContent.files[fileName].dir;
      })
      .map(fileName => ({
        name: fileName,
        file: zipContent.files[fileName]
      }));
    
    console.log(`발견된 이미지 파일: ${imageFiles.length}개`);
    
    if (imageFiles.length === 0) {
      throw new Error('ZIP 파일에서 이미지 파일을 찾을 수 없습니다.');
    }
    
    // 1. 모든 이미지 파일을 먼저 처리하여 해싱된 파일명 목록 생성
    const fileProcessResults = [];
    
    console.log('이미지 파일 전처리 시작...');
    
    for (let i = 0; i < imageFiles.length; i++) {
      const imageFile = imageFiles[i];
      
      try {
        // 1. 파일을 Blob으로 변환
        const originalBlob = await imageFile.file.async('blob');
        
        // 2. PNG인 경우 JPEG로 변환
        let imageBlob = originalBlob;
        const isPng = imageFile.name.toLowerCase().endsWith('.png');
        if (isPng) {
          console.log(`PNG -> JPEG 변환: ${imageFile.name}`);
          imageBlob = await convertPngToJpeg(originalBlob, 0.95);
        }
        
        // 3. 파일명 해싱
        const hashedFileName = await hashFileName(imageFile.name);
        console.log(`파일명 해싱: ${imageFile.name} -> ${hashedFileName}`);
        
        fileProcessResults.push({
          originalFileName: imageFile.name,
          hashedFileName: hashedFileName,
          imageBlob: imageBlob
        });
        
      } catch (error) {
        console.error(`이미지 전처리 실패: ${imageFile.name}`, error);
        throw error;
      }
    }
    
    // 2. 벌크 presigned URL 요청
    console.log('벌크 presigned URL 요청...');
    const fileList = fileProcessResults.map(item => ({
      filename: item.hashedFileName,
      content_type: 'image/jpeg'
    }));
    
    const bulkPresignedData = await getBulkPresignedUrls(fileList);
    console.log(`벌크 presigned URL 받음: ${bulkPresignedData.files?.length}개`);
    
    // 3. 각 파일을 S3에 업로드
    const uploadResults = [];
    const errors = [];
    
    for (let i = 0; i < fileProcessResults.length; i++) {
      const fileResult = fileProcessResults[i];
      const presignedFileData = bulkPresignedData.files[i];
      
      try {
        // 진행상황 콜백 호출
        if (progressCallback) {
          progressCallback({
            current: i + 1,
            total: fileProcessResults.length,
            fileName: fileResult.originalFileName,
            stage: 'uploading'
          });
        }
        
        console.log(`S3 업로드 중: ${fileResult.hashedFileName} (${i + 1}/${fileProcessResults.length})`);
        
        // S3 업로드
        const uploadResult = await uploadToS3WithPresigned(
          presignedFileData.upload_url, 
          fileResult.imageBlob, 
          fileResult.hashedFileName
        );
        
        uploadResults.push({
          originalFileName: fileResult.originalFileName,
          hashedFileName: fileResult.hashedFileName,
          s3Key: presignedFileData.file_key,
          s3Url: presignedFileData.upload_url.split('?')[0], // 쿼리 파라미터 제거한 실제 S3 URL
          success: true
        });
        
        console.log(`업로드 완료: ${fileResult.hashedFileName}`);
        
      } catch (error) {
        console.error(`이미지 업로드 실패: ${fileResult.originalFileName}`, error);
        errors.push({
          fileName: fileResult.originalFileName,
          error: error.message
        });
      }
    }
    
    // 최종 진행상황 콜백
    if (progressCallback) {
      progressCallback({
        current: fileProcessResults.length,
        total: fileProcessResults.length,
        stage: 'completed'
      });
    }
    
    const successCount = uploadResults.length;
    const errorCount = errors.length;
    
    console.log(`이미지 업로드 완료: 성공 ${successCount}개, 실패 ${errorCount}개`);
    
    return {
      success: errorCount === 0,
      data: {
        traceNum: traceNum,
        totalFiles: fileProcessResults.length,
        successCount: successCount,
        errorCount: errorCount,
        uploadedImages: uploadResults,
        errors: errors
      },
      message: `이미지 업로드 완료: 성공 ${successCount}개, 실패 ${errorCount}개`
    };
    
  } catch (error) {
    console.error('개별 이미지 업로드 오류:', error);
    throw error;
  }
};

export default uploadIndividualImages;