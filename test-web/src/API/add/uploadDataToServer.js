import { apiIP } from '../../config';

/**
 * 서버에 CSV와 ZIP 파일을 업로드하는 API
 * @param {Array} data - 테이블 데이터 배열
 * @param {Array} columns - 컬럼 이름 배열  
 * @param {File} zipFile - ZIP 이미지 파일
 * @returns {Promise} - 업로드 결과
 */
export const uploadDataToServer = async (data, columns, zipFile) => {
  try {
    // 1. 데이터 유효성 검사
    if (!data || data.length === 0) {
      throw new Error('업로드할 데이터가 없습니다.');
    }

    if (!zipFile) {
      throw new Error('ZIP 파일이 선택되지 않았습니다.');
    }

    // 2. 매핑 상태 검사 - 모든 데이터가 매핑되어야 함
    const unmappedData = data.filter(row => 
      row['매핑 상태'] === '매핑안됨' || 
      !row['매핑 상태'] || 
      row['매핑 상태'] === ''
    );

    if (unmappedData.length > 0) {
      throw new Error(`매핑되지 않은 데이터가 ${unmappedData.length}개 있습니다. 모든 데이터를 매핑한 후 다시 시도해주세요.`);
    }

    // 3. CSV 문자열 생성
    const csvHeader = columns.join(',') + '\n';
    const csvRows = data.map(row => 
      columns.map(col => {
        const value = row[col] ?? '';
        // CSV에서 콤마, 따옴표, 줄바꿈이 포함된 경우 따옴표로 감싸기
        if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    );
    const csvContent = csvHeader + csvRows.join('\n');

    // 4. FormData 생성
    const formData = new FormData();
    
    // CSV 파일을 Blob으로 생성하여 /label 경로에 저장
    const csvBlob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
    formData.append('label', csvBlob, 'data.csv');
    
    // ZIP 파일을 /image 경로에 저장
    formData.append('image', zipFile, zipFile.name);

    // 5. 서버에 업로드
    const response = await fetch(`http://${apiIP}/mnt/data`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`서버 오류 (${response.status}): ${errorText}`);
    }

    const result = await response.json();
    
    return {
      success: true,
      data: result,
      message: '데이터가 성공적으로 업로드되었습니다.'
    };

  } catch (error) {
    console.error('데이터 업로드 오류:', error);
    
    return {
      success: false,
      error: error.message,
      message: error.message
    };
  }
};

export default uploadDataToServer;
