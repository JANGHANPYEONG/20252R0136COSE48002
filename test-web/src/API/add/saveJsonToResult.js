import { convertExcelToJson, groupSamplesByTrace } from './excelToJsonConverter';

/**
 * result 폴더에 JSON 파일을 저장하는 함수 (개발/테스트용)
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
    
    let jsonData;
    let fileName;
    
    if (excelFile) {
      // 엑셀 파일이 있으면 JSON 변환 사용
      console.log('엑셀 파일에서 JSON 생성 중...');
      const jsonArray = await convertExcelToJson(excelFile, dataFormat);
      const groupedJson = groupSamplesByTrace(jsonArray);
      
      // 하나의 JSON 파일로 저장 (첫 번째 그룹 사용)
      jsonData = groupedJson.length > 0 ? groupedJson[0] : jsonArray[0];
      fileName = `${managementNumber}.json`;
      
      console.log('JSON 변환 완료:', {
        fileName: fileName,
        sampleCount: jsonData.meat ? jsonData.meat.length : 1,
        totalEdgePoints: jsonData.meat ? jsonData.meat.reduce((sum, sample) => sum + Object.keys(sample.edgePoint).length, 0) : 0
      });
    } else {
      // 기존 데이터를 기본 JSON 형식으로 변환
      console.log('기존 데이터를 JSON 형식으로 변환 중...');
      
      // 첫 번째 데이터를 기준으로 JSON 생성
      const firstRow = data[0];
      
      jsonData = {
        userId: "deeplant@example.com",
        rowId: `sheet1-${managementNumber}`,
        meat: {
          traceNum: managementNumber,
          sampleNum: firstRow['샘플번호'] || 'S1',
          gradeNum: firstRow['등급'] || 'X',
          isDeepAging: firstRow['딥에이징'] === 'YES' ? 'Yes' : 'No',
          butcheryDate: firstRow['도축일자'] || '',
          manufactureDate: firstRow['제조(가공)일자'] || '',
          picturedDate: firstRow['촬영일자'] || '',
          period: 'Day7',
          expirationDate: firstRow['소비기한'] || '',
          marbling: parseFloat(firstRow['Marbling']) || 0,
          meatColor: parseFloat(firstRow['Meat Color']) || 0,
          texture: parseFloat(firstRow['Texture']) || 0,
          surfaceMoisture: parseFloat(firstRow['Surface Moisture']) || 0,
          total: parseFloat(firstRow['Total']) || 0,
          edgePoint: {},
          hsi: {
            isRefrigerated: false,
            wavelengthFromFilename: true,
            expectedCount: 0
          }
        }
      };
      
      fileName = `${managementNumber}_basic.json`;
    }

    // 3. JSON 문자열로 변환
    const jsonContent = JSON.stringify(jsonData, null, 2);
    
    // 4. 브라우저 다운로드로 JSON 저장 (로컬 모드)
    console.log('로컬 모드: 브라우저 다운로드로 JSON 저장');
    
    const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    
    return {
      success: true,
      data: {
        fileName: fileName,
        managementNumber: managementNumber,
        dataCount: data.length,
        savedAt: new Date().toISOString(),
        localPath: `Downloads/${fileName}`,
        fileSize: blob.size
      },
      message: `JSON 파일이 다운로드 폴더에 저장되었습니다.\\n파일명: ${fileName}`
    };

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