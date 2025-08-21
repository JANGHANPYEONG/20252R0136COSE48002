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
 * BE에서 presigned URL을 요청하는 함수
 * @param {string} hashedFileName - 해시된 파일명
 * @param {string} contentType - MIME 타입 (기본: image/jpeg)
 * @returns {Promise<Object>} - presigned URL 정보
 */
const getPresignedUrl = async (hashedFileName, contentType = 'image/jpeg') => {
  try {
    const response = await fetch(`http://${apiIP}/upload/presigned-url?filename=${hashedFileName}&content_type=${contentType}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Presigned URL 요청 실패: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;
    
  } catch (error) {
    console.error('Presigned URL 요청 오류:', error);
    throw error;
  }
};

/**
 * Presigned URL을 사용하여 S3에 이미지를 업로드하는 함수
 * @param {Object} presignedData - presigned URL 데이터
 * @param {Blob} imageBlob - 이미지 파일 Blob
 * @returns {Promise<Object>} - 업로드 결과
 */
const uploadToS3WithPresigned = async (presignedData, imageBlob) => {
  try {
    // multipart form data 생성
    const formData = new FormData();
    
    // presigned POST의 fields를 formData에 추가
    Object.keys(presignedData.fields).forEach(key => {
      formData.append(key, presignedData.fields[key]);
    });
    
    // 파일을 마지막에 추가 (중요: 순서가 중요함)
    formData.append('file', imageBlob, presignedData.filename);
    
    // S3에 업로드
    const uploadResponse = await fetch(presignedData.presigned_url, {
      method: 'POST',
      body: formData
    });
    
    if (!uploadResponse.ok) {
      const errorText = await uploadResponse.text();
      throw new Error(`S3 업로드 실패: ${uploadResponse.status} ${errorText}`);
    }
    
    return {
      success: true,
      s3Url: `${presignedData.presigned_url}/${presignedData.key}`,
      key: presignedData.key,
      filename: presignedData.filename
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
    
    // 이미지 파일만 필터링 (jpg, jpeg, png) - RGB 이미지 제외
    const imageFiles = Object.keys(zipContent.files)
      .filter(fileName => {
        const ext = fileName.split('.').pop().toLowerCase();
        const isImageFile = ['jpg', 'jpeg', 'png'].includes(ext) && !zipContent.files[fileName].dir;
        
        // RGB 이미지 제외 (_rgb_ 패턴이 포함된 파일 제외)
        const isRgbImage = fileName.toLowerCase().includes('_rgb_');
        
        return isImageFile && !isRgbImage;
      })
      .map(fileName => ({
        name: fileName,
        file: zipContent.files[fileName]
      }));
    
    console.log(`발견된 이미지 파일: ${imageFiles.length}개`);
    
    if (imageFiles.length === 0) {
      throw new Error('ZIP 파일에서 이미지 파일을 찾을 수 없습니다.');
    }
    
    const uploadResults = [];
    const errors = [];
    
    // 각 이미지 파일을 개별적으로 처리
    for (let i = 0; i < imageFiles.length; i++) {
      const imageFile = imageFiles[i];
      
      try {
        // 진행상황 콜백 호출
        if (progressCallback) {
          progressCallback({
            current: i + 1,
            total: imageFiles.length,
            fileName: imageFile.name,
            stage: 'processing'
          });
        }
        
        console.log(`처리 중: ${imageFile.name} (${i + 1}/${imageFiles.length})`);
        
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
        
        // 4. Presigned URL 요청
        const presignedData = await getPresignedUrl(hashedFileName, 'image/jpeg');
        
        // 5. S3 업로드
        const uploadResult = await uploadToS3WithPresigned(presignedData, imageBlob);
        
        uploadResults.push({
          originalFileName: imageFile.name,
          hashedFileName: hashedFileName,
          s3Key: presignedData.key,
          s3Url: uploadResult.s3Url,
          success: true
        });
        
        console.log(`업로드 완료: ${hashedFileName}`);
        
      } catch (error) {
        console.error(`이미지 업로드 실패: ${imageFile.name}`, error);
        errors.push({
          fileName: imageFile.name,
          error: error.message
        });
      }
    }
    
    // 최종 진행상황 콜백
    if (progressCallback) {
      progressCallback({
        current: imageFiles.length,
        total: imageFiles.length,
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
        totalFiles: imageFiles.length,
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