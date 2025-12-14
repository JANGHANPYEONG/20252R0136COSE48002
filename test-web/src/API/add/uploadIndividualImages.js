import JSZip from 'jszip';
import { apiIP } from '../../config';

/**
 * 파일 경로에서 이력번호+샘플번호를 추출하여 20자리 해시 파일명으로 변환하는 함수
 * @param {string} filePath - 파일 경로 (예: "140119100857_day7/S1/140119100857_s1_430nm.png")
 * @returns {Promise<string|null>} - 해시된 파일명 (예: "e3b3ff1e7a200b6274c4_430nm.png") 또는 null
 */
const hashFileName = async (filePath) => {
  // 파일 경로를 정리하여 파일명과 폴더 구조 분석
  const pathParts = filePath.split('/').filter(part => part.length > 0);
  const fileName = pathParts[pathParts.length - 1]; // 마지막이 파일명
  
  // 파장 정보 추출 (430nm, 540nm 등, rgb 제외)
  const wavelengthMatch = fileName.match(/(\d{3,4}nm)/i);
  const wavelength = wavelengthMatch ? wavelengthMatch[1].toLowerCase() : '';
  
  if (!wavelength) {
    console.warn('파장 정보를 찾을 수 없습니다:', filePath);
    return null;
  }
  
  let traceNum = '';
  let sampleNum = '';
  
  // 방법 1: 파일명에서 직접 추출 (140119100857_s1_430nm.png)
  const fileNamePattern = fileName.match(/^(\d+)_[sS](\d+)_\d+nm\./i);
  if (fileNamePattern) {
    traceNum = fileNamePattern[1];
    sampleNum = fileNamePattern[2];
  } else {
    // 방법 2: 폴더 구조에서 추출 (140119100857_day7/S1/파일명)
    if (pathParts.length >= 3) {
      const folderName = pathParts[pathParts.length - 3]; // 관리번호 폴더
      const partFolder = pathParts[pathParts.length - 2];  // 부위 폴더 (S1, s1 등)
      
      // 관리번호 추출: _ 앞의 숫자 부분만 가져오기
      let extractedNumber = folderName;
      const underscoreIndex = folderName.indexOf('_');
      if (underscoreIndex > 0) {
        const beforeUnderscore = folderName.substring(0, underscoreIndex);
        if (/^\d+$/.test(beforeUnderscore)) {
          extractedNumber = beforeUnderscore;
        }
      }
      
      // 부위 폴더에서 샘플 번호 추출 (S1, s1 -> 1)
      const sampleMatch = partFolder.match(/^[sS](\d+)$/);
      if (sampleMatch && /^\d+$/.test(extractedNumber)) {
        traceNum = extractedNumber;
        sampleNum = sampleMatch[1];
      }
    }
  }
  
  if (!traceNum || !sampleNum) {
    console.warn('이력번호/샘플번호를 추출할 수 없습니다:', filePath);
    return null;
  }
  
  // 이력번호+샘플번호로 20자리 해시 생성 (JSON과 동일한 로직)
  const { generateHashId } = await import('./hashUtils');
  const hashId = await generateHashId(traceNum, sampleNum);
  
  console.log(`파일 경로 분석: ${filePath} -> 이력번호: ${traceNum}, 샘플: ${sampleNum}, 해시: ${hashId}`);
  
  // 해시ID_파장.png 형식으로 반환
  return `${hashId}_${wavelength}.png`;
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
 * Presigned PUT을 사용하여 S3에 이미지를 업로드하는 함수 (헤더 정확히 매칭)
 * @param {string} uploadUrl - S3 presigned PUT URL
 * @param {Blob} imageBlob - 이미지 파일 Blob
 * @param {string} fileName - 파일명
 * @param {string} expectedContentType - 예상되는 Content-Type (presigned URL과 정확히 매칭)
 * @returns {Promise<Object>} - 업로드 결과
 */
const uploadToS3WithPresigned = async (uploadUrl, imageBlob, fileName, expectedContentType) => {
  try {
    console.log(`S3 업로드 시도: ${fileName} (${imageBlob.size} bytes, type: ${imageBlob.type})`);
    
    // expectedContentType을 우선 사용하여 presigned URL과 정확히 매칭
    const actualContentType = expectedContentType || imageBlob.type || 'application/octet-stream';
    const headers = {
      'Content-Type': actualContentType // presigned URL 생성 시와 동일한 타입
    };
    
    console.log('==== S3 업로드 상세 정보 ====');
    console.log('파일명:', fileName);
    console.log('Blob 크기:', imageBlob.size, 'bytes');
    console.log('Blob 원본 타입:', imageBlob.type);
    console.log('기대되는 Content-Type:', expectedContentType);
    console.log('실제 사용할 Content-Type:', actualContentType);
    console.log('업로드 헤더:', headers);
    console.log('업로드 URL (전체):', uploadUrl);
    console.log('업로드 URL (기본):', uploadUrl.split('?')[0]);
    
    // Presigned URL에서 SignedHeaders 확인
    const signedHeadersMatch = uploadUrl.match(/X-Amz-SignedHeaders=([^&]+)/);
    const signedHeaders = signedHeadersMatch ? decodeURIComponent(signedHeadersMatch[1]) : 'none';
    console.log('Presigned URL의 SignedHeaders:', signedHeaders);
    
    // Content-Type이 SignedHeaders에 포함되어 있는지 확인
    const isContentTypeInSigned = signedHeaders.includes('content-type');
    console.log('Content-Type이 서명된 헤더에 포함됨:', isContentTypeInSigned);
    console.log('===============================');
    
    // CORS 문제 해결을 위한 추가 시도
    console.log('fetch 요청 시작...');
    
    try {
      // S3에 PUT 요청으로 업로드
      const uploadResponse = await fetch(uploadUrl, {
        method: 'PUT',
        headers: headers,
        body: imageBlob,
        mode: 'cors', // 명시적으로 CORS 모드 설정
        cache: 'no-cache'
      });
    
    console.log(`S3 응답 상태: ${uploadResponse.status} ${uploadResponse.statusText}`);
    
    if (!uploadResponse.ok) {
      const errorText = await uploadResponse.text();
      console.error(`S3 업로드 실패 상세:`, {
        status: uploadResponse.status,
        statusText: uploadResponse.statusText,
        errorText: errorText,
        fileName: fileName,
        blobType: imageBlob.type,
        blobSize: imageBlob.size
      });
      throw new Error(`S3 업로드 실패: ${uploadResponse.status} ${errorText}`);
    }
    
    console.log(`S3 업로드 성공: ${fileName}`);
    
    return {
      success: true,
      filename: fileName
    };
    
    } catch (fetchError) {
      console.error('==== fetch 요청 자체 오류 ====');
      console.error('오류 타입:', fetchError.name);
      console.error('오류 메시지:', fetchError.message);
      console.error('오류 스택:', fetchError.stack);
      
      if (fetchError.message.includes('CORS')) {
        console.error('CORS 관련 오류 - S3 버킷 CORS 설정 확인 필요');
      } else if (fetchError.message.includes('Failed to fetch')) {
        console.error('네트워크 연결 실패 - 인터넷 연결 또는 URL 확인 필요');
      }
      
      console.error('============================');
      throw fetchError;
    }
    
  } catch (error) {
    console.error('S3 업로드 전체 오류:', error);
    throw error;
  }
};

// JPEG 변환 함수는 더 이상 사용하지 않음 (원본 파일 그대로 업로드)

/**
 * ZIP 파일에서 개별 이미지를 추출하고 해싱하여 S3에 업로드하는 함수
 * @param {File} zipFile - 이미지가 포함된 ZIP 파일
 * @param {string} traceNum - 이력번호 (ZIP에서 추출된 이력번호와 일치 확인용)
 * @param {Function} progressCallback - 진행상황 콜백 함수 (선택사항)
 * @returns {Promise<Object>} - 업로드 결과
 */
export const uploadIndividualImages = async (zipFile, traceNum, progressCallback = null) => {
  try {
    console.log('ZIP 파일 압축 해제 시작...');
    
    // ZIP 파일 압축 해제
    const zip = new JSZip();
    const zipContent = await zip.loadAsync(zipFile);
    
    // 이미지 파일만 필터링 (jpg, jpeg, png) - RGB 파일 제외
    const imageFiles = Object.keys(zipContent.files)
      .filter(fileName => {
        const ext = fileName.split('.').pop().toLowerCase();
        const isValidImage = ['jpg', 'jpeg', 'png'].includes(ext) && !zipContent.files[fileName].dir;
        const isRgbImage = fileName.toLowerCase().includes('_rgb_') || fileName.toLowerCase().includes('rgb');
        
        return isValidImage && !isRgbImage; // RGB 이미지는 제외
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
        // 1. 파일을 Blob으로 변환 (원본 그대로 유지)
        const originalBlob = await imageFile.file.async('blob');
        
        // 2. 파일 타입 결정 (정확한 MIME 타입 매핑)
        const originalExtension = imageFile.name.split('.').pop().toLowerCase();
        const mimeType = originalExtension === 'png' ? 'image/png' : 
                        (originalExtension === 'jpg' || originalExtension === 'jpeg') ? 'image/jpeg' : 
                        'image/png'; // 기본값 (PNG)
        
        // 3. 파일명 해싱 (이력번호+샘플번호 기반 20자리)
        const hashedFileName = await hashFileName(imageFile.name);
        
        if (!hashedFileName) {
          console.warn(`파일명 해싱 실패, 건너뜀: ${imageFile.name}`);
          continue;
        }
        
        console.log(`파일명 해싱: ${imageFile.name} -> ${hashedFileName}`);
        
        fileProcessResults.push({
          originalFileName: imageFile.name,
          hashedFileName: hashedFileName,
          imageBlob: originalBlob, // 원본 Blob 사용
          contentType: mimeType
        });
        
      } catch (error) {
        console.error(`이미지 전처리 실패: ${imageFile.name}`, error);
        throw error;
      }
    }
    
    // 2. 벌크 presigned URL 요청
    console.log('==== BE 요청 데이터 준비 ====');
    const fileList = fileProcessResults.map(item => ({
      filename: item.hashedFileName,
      content_type: item.contentType // 각 파일의 원본 타입 사용
    }));
    
    console.log('BE로 전송할 파일 목록:');
    fileList.forEach((file, index) => {
      console.log(`${index + 1}. ${file.filename} (${file.content_type})`);
    });
    console.log('===============================');
    
    console.log('벌크 presigned URL 요청 중...');
    
    const bulkPresignedData = await getBulkPresignedUrls(fileList);
    console.log(`벌크 presigned URL 받음: ${bulkPresignedData.files?.length}개`);
    
    // presigned URL 응답 상세 로깅
    console.log('==== BE presigned URL 응답 분석 ====');
    console.log('전체 응답:', bulkPresignedData);
    
    if (bulkPresignedData.files && bulkPresignedData.files.length > 0) {
      const firstFile = bulkPresignedData.files[0];
      console.log('첫 번째 파일 정보:');
      console.log('- file_key:', firstFile.file_key);
      console.log('- upload_url 기본부:', firstFile.upload_url?.split('?')[0]);
      
      // URL 파라미터 분석
      const urlParams = new URLSearchParams(firstFile.upload_url?.split('?')[1] || '');
      console.log('- X-Amz-SignedHeaders:', urlParams.get('X-Amz-SignedHeaders'));
      console.log('- X-Amz-Algorithm:', urlParams.get('X-Amz-Algorithm'));
      console.log('- X-Amz-Credential:', urlParams.get('X-Amz-Credential')?.split('/')[0] + '/...');
      console.log('- X-Amz-Date:', urlParams.get('X-Amz-Date'));
      console.log('- X-Amz-Expires:', urlParams.get('X-Amz-Expires'), 'seconds');
      
      // Content-Type 관련 정보 확인
      const signedHeaders = urlParams.get('X-Amz-SignedHeaders') || '';
      const hasContentType = signedHeaders.includes('content-type');
      console.log('- Content-Type이 서명에 포함됨:', hasContentType);
      
      if (hasContentType) {
        console.log('⚠️  Presigned URL에 content-type이 서명되어 있음. 정확한 Content-Type 매칭 필요!');
      } else {
        console.log('ℹ️  Presigned URL에 content-type이 서명되지 않음. 헤더 자유도 높음.');
      }
    }
    console.log('=====================================');
    
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
        
        // S3 직접 업로드 - presigned PUT URL 사용 (정확한 Content-Type 전달)
        const uploadResult = await uploadToS3WithPresigned(
          presignedFileData.upload_url,
          fileResult.imageBlob, 
          fileResult.hashedFileName,
          fileResult.contentType  // 확장자로 결정했던 MIME 타입을 그대로 사용
        );
        
        uploadResults.push({
          originalFileName: fileResult.originalFileName,
          hashedFileName: fileResult.hashedFileName,
          s3Key: presignedFileData.file_key,
          s3Url: presignedFileData.upload_url.split('?')[0],
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