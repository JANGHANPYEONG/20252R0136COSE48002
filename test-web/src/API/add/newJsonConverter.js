import { generateHashId, getSpectralIndex } from './hashUtils';
import { getCategoryId } from '../../Utils/categoryMapping';

/**
 * JSON 데이터를 로컬 result 폴더에 저장하는 함수
 * @param {Object} jsonData - 저장할 JSON 데이터
 * @param {string} traceNum - 이력번호
 * @returns {Promise<Object>} - 저장 결과
 */
const saveJsonToLocal = async (jsonData, traceNum) => {
  try {
    const fileName = `${traceNum}.json`;
    const jsonContent = JSON.stringify(jsonData, null, 2);
    
    // 방법 1: 로컬 서버 API 시도
    try {
      const response = await fetch('http://localhost:3001/api/save-multiple-json', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          files: [{
            fileName: fileName,
            content: jsonContent
          }]
        })
      });

      if (response.ok) {
        const result = await response.json();
        return {
          success: true,
          filePath: result.targetPath || `C:\\sanhak\\20252R0136COSE48002\\test-web\\test-data\\result\\${fileName}`,
          message: `JSON 파일이 로컬 서버를 통해 저장되었습니다: ${fileName}`
        };
      }
    } catch (serverError) {
      console.warn('로컬 서버 연결 실패, 브라우저 저장 시도:', serverError);
    }
    
    // 방법 2: 브라우저 다운로드 API 사용 (하지만 result 폴더명으로)
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
      filePath: `Downloads/${fileName}`,
      message: `로컬 서버 미연결. JSON 파일이 다운로드되었습니다: ${fileName}`,
      fallback: true
    };

  } catch (error) {
    console.error('JSON 저장 실패:', error);
    
    return {
      success: false,
      error: error.message,
      message: `JSON 저장 실패: ${error.message}`
    };
  }
};

/**
 * 엑셀 데이터를 새로운 BE API 형식의 JSON으로 변환하는 함수
 * @param {File} excelFile - 엑셀 파일
 * @param {string} dataFormat - 데이터 형식 ('HSI' 또는 'RGB') 
 * @param {Object} imageMapping - 이미지 매핑 정보 (선택사항)
 * @returns {Promise<Object>} - 변환된 JSON 데이터
 */
export const convertToNewJsonFormat = async (excelFile, dataFormat = 'HSI', imageMapping = null) => {
  try {
    // 1. 엑셀 파일을 JSON으로 변환 (기존 로직 재사용)
    const { convertExcelToJson } = await import('./excelToJsonConverter');
    const excelJsonArray = await convertExcelToJson(excelFile, dataFormat);
    
    console.log('엑셀 데이터 변환 완료:', excelJsonArray.length, '개 샘플');
    console.log('첫 번째 샘플 구조:', excelJsonArray[0]);
    
    // 2. 새로운 형식으로 데이터 변환
    const dataList = [];
    
    for (const sampleData of excelJsonArray) {
      try {
        // 기본 정보 추출 (excelToJsonConverter에서 생성된 구조 고려)
        const traceNum = sampleData.meat?.traceNum || sampleData.traceNum || sampleData.이력번호;
        const sampleNum = sampleData.meat?.sampleNum || sampleData.샘플번호 || sampleData.부위번호;
        
        if (!traceNum || !sampleNum) {
          console.warn('필수 데이터 누락:', { 
            traceNum, 
            sampleNum,
            sampleDataKeys: Object.keys(sampleData),
            meatKeys: sampleData.meat ? Object.keys(sampleData.meat) : 'meat 객체 없음'
          });
          continue;
        }
        
        // 해시 ID 생성 (20자리)
        const hashId = await generateHashId(traceNum, sampleNum);
        
        // 촬영일자에서 Day 정보 추출하여 isRefrigerated 결정
        const picturedDate = sampleData.meat?.picturedDate || sampleData.picturedDate || sampleData.촬영일자 || '';
        const isRefrigerated = picturedDate.includes('Day7') || picturedDate.includes('day7');
        
        // gradeNum 처리 (X면 null, 이외는 그대로)
        const originalGradeNum = sampleData.meat?.gradeNum || sampleData.등급;
        const gradeNum = originalGradeNum === 'X' ? null : originalGradeNum;
        
        // 부위 정보로 categoryId 생성
        const partName = sampleData.meat?.part || sampleData.부위 || sampleData.meat?.sampleNum || sampleData.샘플번호;
        const speciesName = sampleData.meat?.species || sampleData.축종 || sampleData.품종;
        const categoryId = getCategoryId(partName, speciesName);
        
        // seqno 결정 (딥에이징이 NO면 0, YES면 1)
        const isDeepAging = sampleData.meat?.isDeepAging || sampleData.딥에이징 || 'No';
        const seqno = isDeepAging.toLowerCase() === 'yes' || isDeepAging === 'YES' ? 1 : 0;
        
        // bands 데이터 생성
        const bands = [];
        
        // edgePoint 정보 가져오기 (기존 JSON에서)
        const edgePoint = sampleData.meat?.edgePoint || {};
        
        if (imageMapping && imageMapping[traceNum] && imageMapping[traceNum][sampleNum.replace(/[sS]/g, '')]) {
          const sampleImages = imageMapping[traceNum][sampleNum.replace(/[sS]/g, '')];
          
          // 파장별로 bands 생성 (RGB 제외)
          Object.keys(sampleImages)
            .filter(wavelength => wavelength.toLowerCase() !== 'rgb') // RGB 제외
            .sort()
            .forEach(wavelength => {
              const spectralIndex = getSpectralIndex(wavelength);
              
              const bandData = {
                spectral_index: spectralIndex,
                topLeft: edgePoint[`TL (${wavelength})`] || [0, 0],
                topRight: edgePoint[`TR (${wavelength})`] || [0, 0], 
                bottomRight: edgePoint[`BR (${wavelength})`] || [0, 0],
                bottomLeft: edgePoint[`BL (${wavelength})`] || [0, 0],
                filename: `${hashId}_${wavelength}.png` // 해시ID_파장대.png 형식
              };
              
              bands.push(bandData);
            });
        } else {
          // 이미지 매핑이 없는 경우 HSI 기본 파장대만 생성 (RGB 제외)
          if (dataFormat === 'HSI') {
            // HSI의 경우 기본 파장대 생성
            ['430nm', '540nm'].forEach((wavelength, index) => {
              bands.push({
                spectral_index: index,
                topLeft: edgePoint[`TL (${wavelength})`] || [0, 0],
                topRight: edgePoint[`TR (${wavelength})`] || [0, 0],
                bottomRight: edgePoint[`BR (${wavelength})`] || [0, 0], 
                bottomLeft: edgePoint[`BL (${wavelength})`] || [0, 0],
                filename: `${hashId}_${wavelength}.png`
              });
            });
          }
          // RGB 형식인 경우 bands를 빈 배열로 유지 (RGB 데이터 제외)
        }
        
        // 새로운 형식의 데이터 객체 생성
        const newSampleData = {
          userId: "deeplant@example.com", // 하드코딩
          id: hashId, // 20자리 해시 ID
          traceNum: traceNum,
          butcheryYmd: sampleData.meat?.butcheryDate || sampleData.butcheryDate || sampleData.도축일자 || "2025-08-05",
          manufactureYmd: sampleData.meat?.manufactureDate || sampleData.manufactureDate || sampleData.제조일자 || sampleData["제조(가공)일자"] || "2025-08-06", 
          filmedAt: sampleData.meat?.picturedDate || sampleData.picturedDate || sampleData.촬영일자 || "2025-08-18",
          expireYmd: sampleData.meat?.expirationDate || sampleData.expirationDate || sampleData.소비기한 || "2025-09-19",
          isRefrigerated: isRefrigerated,
          meat: {
            categoryId: categoryId >= 0 ? categoryId : 0, // 부위명으로 생성된 categoryId, 실패시 기본값 0
            gradeNum: gradeNum,
            seqno: seqno,
            marbling: parseInt(sampleData.meat?.marbling || sampleData.마블링 || 0),
            meat_color: parseInt(sampleData.meat?.meatColor || sampleData.육색 || 0), 
            texture: parseInt(sampleData.meat?.texture || sampleData.조직감 || 0),
            surface_moisture: parseInt(sampleData.meat?.surfaceMoisture || sampleData.표면수분 || 0),
            overall: parseInt(sampleData.meat?.total || sampleData.종합 || 0),
            bands: bands
          }
        };
        
        dataList.push(newSampleData);
        console.log(`샘플 변환 완료: ${traceNum}_${sampleNum} -> ${hashId}`);
        
      } catch (error) {
        console.error('샘플 데이터 변환 오류:', error, sampleData);
      }
    }
    
    console.log(`전체 변환 완료: ${dataList.length}개 샘플`);
    
    // 최종 JSON 데이터 (로컬 저장과 BE 전송에 동일하게 사용)
    const finalJsonData = { data_list: dataList };
    
    // 로컬 폴더에 JSON 파일 저장 (test-data/result에만 저장)
    let localSaveResult = null;
    try {
      localSaveResult = await saveJsonToLocal(finalJsonData, dataList[0]?.traceNum || 'unknown');
      
      if (!localSaveResult.success) {
        console.warn('로컬 저장 실패:', localSaveResult.message);
      }
    } catch (localError) {
      console.warn('로컬 저장 오류:', localError);
      localSaveResult = {
        success: false,
        error: localError.message,
        message: `로컬 저장 실패: ${localError.message}`
      };
    }
    
    return {
      success: true,
      data: finalJsonData, // 로컬 저장과 동일한 데이터 반환
      localSave: localSaveResult,
      message: `${dataList.length}개 샘플이 새로운 형식으로 변환되었습니다.${localSaveResult?.success ? `\n로컬 저장: ${localSaveResult.filePath}` : ''}`
    };
    
  } catch (error) {
    console.error('JSON 변환 오류:', error);
    return {
      success: false,
      error: error.message,
      message: `JSON 변환 실패: ${error.message}`
    };
  }
};

/**
 * 새로운 형식의 JSON을 BE로 전송하는 함수
 * @param {Object} jsonData - 전송할 JSON 데이터 ({ data_list: [...] })
 * @param {string} traceNum - 이력번호
 * @returns {Promise<Object>} - 전송 결과
 */
export const sendNewJsonToBackend = async (jsonData, traceNum) => {
  try {
    console.log('BE로 새로운 형식의 JSON 데이터 전송 시작...', { 
      traceNum, 
      dataCount: jsonData.data_list?.length,
      firstSample: jsonData.data_list?.[0] // 첫 번째 샘플 구조 확인
    });
    
    // 전송할 JSON 데이터를 문자열로 변환하여 확인
    const jsonString = JSON.stringify(jsonData, null, 2);
    console.log('BE로 전송할 JSON 데이터 (전체):', jsonString.substring(0, 1000) + '...');
    
    const { apiIP } = await import('../../config');
    
    // const response = await fetch(`http://${apiIP}/data-upload/bulk-upsert`, {
    const response = await fetch(`http://${apiIP}/data-upload/bulk-upload`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonString // JSON 문자열로 직접 전송
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
      message: `이력번호 ${traceNum}의 ${jsonData.data_list.length}개 샘플 데이터가 BE로 전송되었습니다.`
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