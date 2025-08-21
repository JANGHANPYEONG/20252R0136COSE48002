import { convertExcelToJson, createIndividualSampleJsons } from './excelToJsonConverter';

/**
 * 샘플별 개별 JSON 파일을 result 폴더에 저장하는 함수
 * @param {Array} data - 테이블 데이터 배열
 * @param {Array} columns - 컬럼 이름 배열  
 * @param {File} zipFile - ZIP 이미지 파일
 * @param {string} dataFormat - 데이터 형식 ('HSI' 또는 'RGB')
 * @param {File} excelFile - 엑셀 파일 (선택사항)
 * @returns {Promise} - 저장 결과
 */
export const saveJsonToResult = async (data, columns, zipFile, dataFormat = 'HSI', excelFile = null) => {
  try {
    // 1. 데이터 유효성 검사
    if (!data || data.length === 0) {
      throw new Error('저장할 데이터가 없습니다.');
    }

    // 2. 이력번호 추출 (첫 번째 데이터에서)
    const managementNumber = data.length > 0 ? data[0]['이력번호'] : 'unknown';
    
    if (!excelFile) {
      throw new Error('엑셀 파일이 필요합니다. 샘플별 JSON 생성을 위해서는 엑셀 파일을 업로드해주세요.');
    }

    // 3. 엑셀 파일에서 샘플별 JSON 생성
    console.log('엑셀 파일에서 샘플별 JSON 생성 중...');
    const jsonArray = await convertExcelToJson(excelFile, dataFormat);
    const individualJsons = createIndividualSampleJsons(jsonArray);
    
    console.log('JSON 변환 완료:', {
      totalSamples: individualJsons.length,
      files: individualJsons.map(item => item.fileName)
    });
    
    // 4. 서버에 여러 JSON 파일 저장 요청
    console.log('result 폴더에 샘플별 JSON 파일들 저장 중...');
    
    const filesData = individualJsons.map(item => ({
      fileName: item.fileName,
      content: JSON.stringify(item.data, null, 2)
    }));

    try {
      const response = await fetch('http://localhost:3001/api/save-multiple-json', {  // 대응하는 backend API 구현되어 있지 않음.
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ files: filesData })
      });

      if (!response.ok) {
        throw new Error(`서버 응답 오류: ${response.status}`);
      }

      const result = await response.json();
      
      console.log('result 폴더 저장 완료:', result);

      return {
        success: true,
        data: {
          fileCount: individualJsons.length,
          fileNames: individualJsons.map(item => item.fileName),
          managementNumber: managementNumber,
          dataCount: data.length,
          savedAt: new Date().toISOString(),
          localPath: result.targetPath,
          totalSize: filesData.reduce((sum, file) => sum + file.content.length, 0),
          serverResponse: result
        },
        message: `${individualJsons.length}개의 JSON 파일이 result 폴더에 저장되었습니다.\\n저장 경로: ${result.targetPath}\\n파일명: ${individualJsons.map(item => item.fileName).join(', ')}`
      };

    } catch (serverError) {
      // 서버가 연결되지 않은 경우 브라우저 다운로드로 fallback
      console.warn('서버 연결 실패, 브라우저 다운로드로 대체:', serverError);
      
      for (const jsonItem of individualJsons) {
        const jsonContent = JSON.stringify(jsonItem.data, null, 2);
        
        const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = jsonItem.fileName;
        link.style.display = 'none';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        URL.revokeObjectURL(url);
        
        // 파일 간격을 두어 브라우저가 처리할 시간을 줌
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      return {
        success: true,
        data: {
          fileCount: individualJsons.length,
          fileNames: individualJsons.map(item => item.fileName),
          managementNumber: managementNumber,
          dataCount: data.length,
          savedAt: new Date().toISOString(),
          localPath: `Downloads/`,
          totalSize: filesData.reduce((sum, file) => sum + file.content.length, 0),
          fallback: true
        },
        message: `서버 연결 실패. ${individualJsons.length}개의 JSON 파일이 다운로드 폴더에 저장되었습니다.\\n서버를 시작하려면: npm run json-server\\n파일명: ${individualJsons.map(item => item.fileName).join(', ')}`
      };
    }

  } catch (error) {
    console.error('JSON 저장 오류:', error);
    
    return {
      success: false,
      error: error.message,
      message: `JSON 저장 실패: ${error.message}`
    };
  }
};

/**
 * BE로 JSON 데이터를 전송하는 함수
 * @param {Object} jsonData - 전송할 JSON 데이터 (data_list 형태)
 * @param {string} traceNum - 이력번호
 * @returns {Promise<Object>} - 전송 결과
 */
export const sendJsonToBackend = async (jsonData, traceNum) => {
  try {
    console.log('BE로 JSON 데이터 전송 시작...', { 
      traceNum, 
      dataCount: jsonData.data_list?.length,
      sampleData: jsonData.data_list?.[0] // 첫 번째 샘플 구조 확인용
    });
    
    const requestBody = {
      traceNum: traceNum,
      data_list: jsonData.data_list
    };
    
    console.log('전송할 데이터 구조:', {
      traceNum: requestBody.traceNum,
      requestBodyKeys: Object.keys(requestBody),
      dataListLength: requestBody.data_list?.length,
      firstItemKeys: requestBody.data_list?.[0] ? Object.keys(requestBody.data_list[0]) : 'none'
    });
    
    const response = await fetch(`http://${apiIP}/data-upload/bulk-upload`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('BE 응답 오류 상세:', {
        status: response.status,
        statusText: response.statusText,
        errorBody: errorText
      });
      throw new Error(`BE 응답 오류: ${response.status} ${response.statusText} - ${errorText}`);
    }

    const result = await response.json();
    
    console.log('BE 전송 성공:', result);
    
    return {
      success: true,
      data: result,
      message: `이력번호 ${traceNum}의 데이터가 BE로 전송되었습니다.`
    };

  } catch (error) {
    console.error('BE 전송 오류:', error);
    
    return {
      success: false,
      error: error.message,
      message: `BE 전송 실패: ${error.message}`
    };
  }
};

/**
 * 샘플별 개별 JSON 파일을 result 폴더에 저장하고 BE로 전송하는 통합 함수
 * @param {Array} data - 테이블 데이터 배열
 * @param {Array} columns - 컬럼 이름 배열  
 * @param {File} zipFile - ZIP 이미지 파일
 * @param {string} dataFormat - 데이터 형식 ('HSI' 또는 'RGB')
 * @param {File} excelFile - 엑셀 파일 (선택사항)
 * @param {boolean} sendToBE - BE로 전송 여부 (기본값: false)
 * @returns {Promise} - 저장 및 전송 결과
 */
export const saveAndSendJsonData = async (data, columns, zipFile, dataFormat = 'HSI', excelFile = null, sendToBE = false) => {
  try {
    // 1. 기본 JSON 저장
    const saveResult = await saveJsonToResult(data, columns, zipFile, dataFormat, excelFile);
    
    if (!saveResult.success) {
      return saveResult;
    }

    // 2. BE 전송 (선택적)
    let beResult = null;
    if (sendToBE && saveResult.data?.managementNumber) {
      try {
        // 저장된 JSON 파일 읽기
        const managementNumber = saveResult.data.managementNumber;
        const savedJsonPath = `test-data/result/${managementNumber}.json`;
        
        // 파일을 직접 읽지 말고 이미 생성된 데이터를 사용
        const jsonArray = await convertExcelToJson(excelFile, dataFormat);
        const individualJsons = await mapImageFilenamesToJsons(
          createIndividualSampleJsons(jsonArray), 
          zipFile
        );
        
        if (individualJsons.length > 0) {
          const jsonData = individualJsons[0].data; // 첫 번째 (그리고 유일한) JSON 데이터
          beResult = await sendJsonToBackend(jsonData, managementNumber);
        }
        
      } catch (beError) {
        console.warn('BE 전송 실패했지만 로컬 저장은 완료:', beError);
        beResult = {
          success: false,
          error: beError.message,
          message: `로컬 저장 완료, BE 전송 실패: ${beError.message}`
        };
      }
    }

    // 3. 통합 결과 반환
    return {
      success: true,
      data: {
        ...saveResult.data,
        beTransmission: beResult
      },
      message: beResult 
        ? `${saveResult.message}\n${beResult.message}`
        : saveResult.message
    };

  } catch (error) {
    console.error('JSON 저장/전송 오류:', error);
    
    return {
      success: false,
      error: error.message,
      message: `JSON 저장/전송 실패: ${error.message}`
    };
  }
};
