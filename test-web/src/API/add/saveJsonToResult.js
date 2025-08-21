import { convertExcelToJson, createIndividualSampleJsons } from './excelToJsonConverter';
import { apiIP } from '../../config';
import JSZip from 'jszip';

/**
 * 파일명을 SHA-256 해시로 변환하는 함수 (uploadIndividualImages.js와 동일)
 * @param {string} originalFileName - 원본 파일명 (예: "140119100857_s1_430nm.png")
 * @returns {Promise<string>} - 해시된 파일명 (예: "abc123def_430nm.jpg")
 */
const hashFileName = async (originalFileName) => {
  // 파장 정보 추출 (430nm, 540nm 등)
  const wavelengthMatch = originalFileName.match(/(\d{3,4}nm)/i);
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
 * 이미지 파일명과 JSON bands의 filename을 매핑하는 함수
 * @param {Array} individualJsons - 개별 JSON 배열
 * @param {File} zipFile - ZIP 파일
 * @returns {Promise<Array>} - filename이 업데이트된 JSON 배열
 */
const mapImageFilenamesToJsons = async (individualJsons, zipFile) => {
  if (!zipFile) {
    console.log('ZIP 파일이 없으므로 filename 매핑을 건너뜁니다.');
    return individualJsons;
  }

  try {
    console.log('이미지 파일명 매핑 시작...');
    
    // ZIP 파일에서 이미지 파일 목록 추출
    const zip = new JSZip();
    const zipContent = await zip.loadAsync(zipFile);
    
    // HSI 이미지 파일만 추출 (RGB 제외) - 샘플별 매핑 생성
    const sampleImageMap = {};
    
    for (const [fileName, fileObj] of Object.entries(zipContent.files)) {
      if (fileObj.dir) continue;
      
      const ext = fileName.split('.').pop().toLowerCase();
      const isImageFile = ['jpg', 'jpeg', 'png'].includes(ext);
      const isRgbImage = fileName.toLowerCase().includes('_rgb_');
      
      if (isImageFile && !isRgbImage) {
        // 샘플번호와 파장 정보 추출
        const sampleMatch = fileName.match(/_s(\d+)_/i);
        const wavelengthMatch = fileName.match(/(\d{3,4}nm)/i);
        
        if (sampleMatch && wavelengthMatch) {
          const sampleNumber = parseInt(sampleMatch[1], 10);
          const wavelength = wavelengthMatch[1].toLowerCase();
          
          // 해싱된 파일명 생성
          const hashedFileName = await hashFileName(fileName);
          
          console.log(`이미지 매핑: ${fileName} -> ${hashedFileName} (샘플 ${sampleNumber}, ${wavelength})`);
          
          // 샘플별 매핑 저장
          if (!sampleImageMap[sampleNumber]) {
            sampleImageMap[sampleNumber] = {};
          }
          sampleImageMap[sampleNumber][wavelength] = hashedFileName;
        }
      }
    }
    
    console.log('샘플별 이미지 매핑 완료:', Object.keys(sampleImageMap).length, '개 샘플');
    
    // JSON들의 data_list 내 bands filename 업데이트
    const updatedJsons = individualJsons.map(jsonItem => {
      const updatedData = { ...jsonItem.data };
      
      if (updatedData.data_list && Array.isArray(updatedData.data_list)) {
        updatedData.data_list = updatedData.data_list.map(dataItem => {
          const updatedDataItem = { ...dataItem };
          
          if (updatedDataItem.meat && updatedDataItem.meat.bands) {
            const sampleNumber = updatedDataItem.meat.seqno + 1; // seqno는 0부터 시작하므로 +1
            
            updatedDataItem.meat.bands = updatedDataItem.meat.bands.map(band => {
              // 임시 파일명에서 파장 추출 (예: "430nm.jpg" -> "430nm")
              const wavelength = band.filename.replace('.jpg', '');
              
              // 해당 샘플의 매핑된 해싱 파일명이 있으면 교체
              if (sampleImageMap[sampleNumber] && sampleImageMap[sampleNumber][wavelength]) {
                const hashedFilename = sampleImageMap[sampleNumber][wavelength];
                console.log(`샘플 ${sampleNumber} 파장 ${wavelength} 매핑: ${band.filename} -> ${hashedFilename}`);
                return {
                  ...band,
                  filename: hashedFilename
                };
              }
              
              console.warn(`샘플 ${sampleNumber} 파장 ${wavelength}에 대한 매핑된 이미지 파일을 찾을 수 없습니다.`);
              return band;
            });
          }
          
          return updatedDataItem;
        });
      }
      
      return {
        ...jsonItem,
        data: updatedData
      };
    });
    
    console.log('이미지 파일명 매핑 완료');
    return updatedJsons;
    
  } catch (error) {
    console.error('이미지 파일명 매핑 오류:', error);
    return individualJsons; // 오류 시 원본 반환
  }
};

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
    let individualJsons = createIndividualSampleJsons(jsonArray);
    
    // 4. 이미지 파일명 매핑 (해싱된 파일명으로 업데이트)
    console.log('이미지 파일명 매핑 중...');
    individualJsons = await mapImageFilenamesToJsons(individualJsons, zipFile);
    
    console.log('JSON 변환 완료:', {
      totalSamples: individualJsons.length,
      files: individualJsons.map(item => item.fileName)
    });
    
    // 5. 서버에 여러 JSON 파일 저장 요청
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

/**
 * BE로 JSON 데이터를 전송하는 함수
 * @param {Object} jsonData - 전송할 JSON 데이터 (data_list 형태)
 * @param {string} traceNum - 이력번호
 * @returns {Promise<Object>} - 전송 결과
 */
export const sendJsonToBackend = async (jsonData, traceNum) => {
  try {
    console.log('BE로 JSON 데이터 전송 시작...', { traceNum, dataCount: jsonData.data_list?.length });
    
    const response = await fetch(`http://${apiIP}/meat/add/json-data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        traceNum: traceNum,
        data: jsonData
      })
    });

    if (!response.ok) {
      throw new Error(`BE 응답 오류: ${response.status} ${response.statusText}`);
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

export default saveJsonToResult;