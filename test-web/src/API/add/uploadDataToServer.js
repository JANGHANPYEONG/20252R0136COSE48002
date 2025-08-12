import { apiIP, STORAGE_CONFIG } from '../../config';

/**
 * 서버에 CSV와 ZIP 파일을 업로드하는 API
 * Ubuntu 서버의 /home/ubuntu/2025-Deeplant-Dev/database/image 및 label 경로에 저장
 * @param {Array} data - 테이블 데이터 배열
 * @param {Array} columns - 컬럼 이름 배열  
 * @param {File} zipFile - ZIP 이미지 파일
 * @param {string} dataFormat - 데이터 형식 ('HSI' 또는 'RGB')
 * @returns {Promise} - 업로드 결과
 */
export const uploadDataToServer = async (data, columns, zipFile, dataFormat = 'HSI') => {
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

    // 3. 서버 설정 가져오기
    const serverConfig = STORAGE_CONFIG.server;
    
    // 4. 이력번호 추출 (첫 번째 데이터에서)
    const managementNumber = data.length > 0 ? data[0]['이력번호'] : 'unknown';
    
    // 5. "매핑 상태" 컬럼 제외하고 CSV 생성
    const filteredColumns = columns.filter(col => col !== '매핑 상태');
    const csvHeader = filteredColumns.join(',') + '\n';
    const csvRows = data.map(row => 
      filteredColumns.map(col => {
        const value = row[col] ?? '';
        // CSV에서 콤마, 따옴표, 줄바꿈이 포함된 경우 따옴표로 감싸기
        if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
          return `"${value.replace(/"/g, '""')}"`;
        }
        return value;
      }).join(',')
    );
    const csvContent = csvHeader + csvRows.join('\n');

    // 6. FormData 생성
    const formData = new FormData();
    
    // CSV 파일을 Blob으로 생성하여 label 경로에 저장 (이력번호 파일명 사용)
    const csvBlob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
    const csvFileName = `${managementNumber}.csv`;
    formData.append('label', csvBlob, csvFileName);
    
    // ZIP 파일을 image 경로에 저장 (원본 파일명 유지)
    formData.append('image', zipFile, zipFile.name);
    
    // 서버 경로 정보 추가
    formData.append('basePath', serverConfig.basePath);
    formData.append('csvPath', serverConfig.csvPath);
    formData.append('imagePath', serverConfig.imagePath);
    
    // 데이터 형식 정보 추가
    formData.append('dataFormat', dataFormat);

    console.log('업로드 시작:', {
      serverIP: apiIP,
      endpoint: serverConfig.endpoint,
      basePath: serverConfig.basePath,
      csvFile: csvFileName,
      zipFile: zipFile.name,
      managementNumber: managementNumber,
      dataCount: data.length,
      dataFormat: dataFormat,
      excludedColumns: ['매핑 상태']
    });

    // 6. 서버에 업로드
    const response = await fetch(`http://${apiIP}${serverConfig.endpoint}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      const errorData = JSON.parse(errorText);
      
      // 409 충돌 오류 (중복 파일)인 경우 사용자에게 선택권 제공
      if (response.status === 409) {
        const userChoice = window.confirm(
          `${errorData.message}\n\n기존 파일을 덮어쓰시겠습니까?\n\n확인: 덮어쓰기\n취소: 업로드 중단`
        );
        
        if (userChoice) {
          // 덮어쓰기 요청 (overwrite=true 파라미터 추가)
          formData.append('overwrite', 'true');
          
          const retryResponse = await fetch(`http://${apiIP}${serverConfig.endpoint}`, {
            method: 'POST',
            body: formData,
          });
          
          if (!retryResponse.ok) {
            const retryErrorText = await retryResponse.text();
            throw new Error(`서버 오류 (${retryResponse.status}): ${retryErrorText}`);
          }
          
          // 재시도 성공 시 결과 처리
          const retryResult = await retryResponse.json();
          return {
            success: true,
            data: {
              ...retryResult,
              csvPath: `${serverConfig.basePath}/${serverConfig.csvPath}/${csvFileName}`,
              imagePath: `${serverConfig.basePath}/${serverConfig.imagePath}/${zipFile.name}`,
              uploadedAt: new Date().toISOString(),
              dataCount: data.length,
              overwritten: true
            },
            message: `기존 파일을 덮어써서 업로드했습니다.\n- CSV: ${serverConfig.csvPath}/${csvFileName}\n- 이미지: ${serverConfig.imagePath}/${zipFile.name}`
          };
        } else {
          // 사용자가 취소한 경우
          throw new Error('사용자가 업로드를 취소했습니다.');
        }
      } else {
        throw new Error(`서버 오류 (${response.status}): ${errorText}`);
      }
    }

    const result = await response.json();
    
    console.log('업로드 성공:', result);
    
    return {
      success: true,
      data: {
        ...result,
        csvPath: `${serverConfig.basePath}/${serverConfig.csvPath}/${csvFileName}`,
        imagePath: `${serverConfig.basePath}/${serverConfig.imagePath}/${zipFile.name}`,
        uploadedAt: new Date().toISOString(),
        dataCount: data.length
      },
      message: `데이터가 성공적으로 업로드되었습니다.\n- CSV: ${serverConfig.csvPath}/${csvFileName}\n- 이미지: ${serverConfig.imagePath}/${zipFile.name}`
    };

  } catch (error) {
    console.error('데이터 업로드 오류:', error);
    
    return {
      success: false,
      error: error.message,
      message: `업로드 실패: ${error.message}`
    };
  }
};

export default uploadDataToServer;
