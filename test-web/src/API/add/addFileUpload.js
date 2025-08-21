import { apiIP } from '../../config';

// 파일 업로드 API (이미지 + CSV)
export const addFileUpload = async (
  file, // 업로드할 파일 (이미지 또는 CSV)
  meatId, // 이력번호
  userId, // 사용자 ID
  fileType, // 'image' 또는 'csv'
  description = '' // 파일 설명 (선택사항)
) => {
  try {
    // 1. 파일 유효성 검사
    if (!file) {
      throw new Error('업로드할 파일이 없습니다.');
    }

    // 파일 크기 제한 (10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      throw new Error('파일 크기가 10MB를 초과할 수 없습니다.');
    }

    // 파일 타입 검증
    const allowedImageTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp'];
    const allowedCsvTypes = ['text/csv', 'application/vnd.ms-excel'];
    
    if (fileType === 'image' && !allowedImageTypes.includes(file.type)) {
      throw new Error('지원하지 않는 이미지 형식입니다. (JPEG, PNG, BMP만 지원)');
    }
    
    if (fileType === 'csv' && !allowedCsvTypes.includes(file.type) && !file.name.endsWith('.csv')) {
      throw new Error('지원하지 않는 파일 형식입니다. (CSV만 지원)');
    }

    // 2. FormData 생성
    const formData = new FormData();
    formData.append('file', file);
    formData.append('meatId', meatId);
    formData.append('userId', userId);
    formData.append('fileType', fileType);
    formData.append('description', description);

    // 3. 서버에 파일 업로드 (/mnt/data 경로에 저장)
    const response = await fetch(`http://${apiIP}/mnt/data`, {
      method: 'POST',
      body: formData, // FormData는 Content-Type 헤더를 자동으로 설정
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || '파일 업로드 중 오류가 발생했습니다.');
    }

    const responseData = await response.json();
    
    return {
      success: true,
      data: responseData
    };

  } catch (error) {
    console.error('파일 업로드 오류:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

export default addFileUpload;
