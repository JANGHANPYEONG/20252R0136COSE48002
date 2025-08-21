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
      const response = await fetch('http://localhost:3001/api/save-multiple-json', {
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

export default saveJsonToResult;