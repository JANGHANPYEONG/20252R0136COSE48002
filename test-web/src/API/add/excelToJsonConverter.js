import * as XLSX from 'xlsx';

/**
 * 이력번호와 샘플번호를 결합하여 해시 ID를 생성하는 함수
 * @param {string} traceNum - 이력번호
 * @param {string} sampleNum - 샘플번호
 * @returns {Promise<string>} - 20자리 해시 ID
 */
const generateHashId = async (traceNum, sampleNum) => {
  const combinedString = `${traceNum}_${sampleNum}`;
  const encoder = new TextEncoder();
  const data = encoder.encode(combinedString);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  
  // 20자리 해시 ID 반환
  return hashHex.substring(0, 20);
};

/**
 * 엑셀 파일을 ex.json 형식으로 변환하는 함수
 * @param {File} excelFile - 엑셀 파일
 * @param {string} dataFormat - 데이터 형식 ('HSI' 또는 'RGB')
 * @returns {Promise<Array>} - 변환된 JSON 배열
 */
export const convertExcelToJson = async (excelFile, dataFormat = 'HSI') => {
  try {
    // 엑셀 파일 읽기
    const arrayBuffer = await excelFile.arrayBuffer();
    const workbook = XLSX.read(arrayBuffer, { type: 'array' });
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

    if (!data || data.length < 2) {
      throw new Error('엑셀 파일에 데이터가 없습니다.');
    }

    const headers = data[0];
    const rows = data.slice(1).filter(row => row.some(cell => cell !== ''));

    console.log('엑셀 헤더:', headers);
    console.log('데이터 행 수:', rows.length);

    // 헤더 매핑
    const headerMap = createHeaderMap(headers);
    
    // 각 행을 JSON으로 변환
    const jsonData = [];
    
    for (const row of rows) {
      if (!row[headerMap.traceNum] || !row[headerMap.sampleNum]) continue;
      
      const traceNum = String(row[headerMap.traceNum]).trim();
      const sampleNum = String(row[headerMap.sampleNum]).trim();
      
      // 해시 ID 생성
      const hashId = await generateHashId(traceNum, sampleNum);
      
      // 촬영일자에서 isRefrigerated 판단
      const picturedDateValue = row[headerMap.picturedDate];
      const isRefrigerated = parseIsRefrigerated(picturedDateValue);
      
      // 등급 처리 (X인 경우 null로 변환)
      const gradeNum = row[headerMap.grade];
      const processedGrade = (gradeNum === 'X' || gradeNum === 'x') ? null : gradeNum;
      
      // 딥에이징 컬럼에서 seqno 결정 (NO=0, YES=1)
      const deepAgingValue = row[headerMap.deepAging];
      const seqno = parseDeepAging(deepAgingValue);
      
      // 파장별 좌표 데이터 추출 (RGB 제외)
      const bands = extractBands(row, headerMap, headers);
      
      const jsonItem = {
        userId: "deeplant@example.com",
        id: hashId,
        traceNum: traceNum,
        sampleNum: sampleNum, // 샘플번호 추가 (파일명 생성용)
        butcheryYmd: formatDate(row[headerMap.butcheryDate]),
        manufactureYmd: formatDate(row[headerMap.manufactureDate]),
        filmedAt: formatDate(row[headerMap.picturedDate]),
        expireYmd: formatDate(row[headerMap.expirationDate]),
        isRefrigerated: isRefrigerated,
        meat: {
          categoryId: mapPartToCategoryId(row[headerMap.part]),
          gradeNum: processedGrade,
          seqno: seqno,
          marbling: parseFloat(row[headerMap.marbling]) || 0,
          meat_color: parseFloat(row[headerMap.meatColor]) || 0,
          texture: parseFloat(row[headerMap.texture]) || 0,
          surface_moisture: parseFloat(row[headerMap.surfaceMoisture]) || 0,
          overall: parseFloat(row[headerMap.total]) || 0,
          bands: bands
        }
      };

      jsonData.push(jsonItem);
    }

    console.log(`엑셀 데이터 변환 완료: ${jsonData.length}개 항목`);
    return jsonData;

  } catch (error) {
    console.error('엑셀 to JSON 변환 오류:', error);
    throw new Error(`엑셀 파일 변환 실패: ${error.message}`);
  }
};

/**
 * 헤더 매핑 생성
 */
const createHeaderMap = (headers) => {
  const map = {};
  
  headers.forEach((header, index) => {
    const h = String(header).trim();
    
    if (h.includes('이력번호') || h.includes('이력')) {
      map.traceNum = index;
    } else if (h.includes('샘플번호') || h.includes('샘플')) {
      map.sampleNum = index;
    } else if (h.includes('부위')) {
      map.part = index;
    } else if (h.includes('등급')) {
      map.grade = index;
    } else if (h.includes('딥에이징')) {
      map.deepAging = index;
    } else if (h.includes('도축일자')) {
      map.butcheryDate = index;
    } else if (h.includes('제조') || h.includes('가공')) {
      map.manufactureDate = index;
    } else if (h.includes('촬영일자')) {
      map.picturedDate = index;
    } else if (h.includes('소비기한')) {
      map.expirationDate = index;
    } else if (h.includes('Marbling') || h.includes('marbling')) {
      map.marbling = index;
    } else if (h.includes('Meat Color') || h.includes('meat color')) {
      map.meatColor = index;
    } else if (h.includes('Texture') || h.includes('texture')) {
      map.texture = index;
    } else if (h.includes('Surface Moisture') || h.includes('surface moisture')) {
      map.surfaceMoisture = index;
    } else if (h.includes('Total') || h.includes('total')) {
      map.total = index;
    }
  });

  return map;
};

/**
 * edgePoint 데이터 추출 (모든 파장 지원)
 */
const extractEdgePoints = (row, headerMap, headers) => {
  const edgePoints = {};
  
  // 파장별 좌표 패턴 찾기
  const wavelengthPatterns = {};
  
  headers.forEach((header, index) => {
    const h = String(header).trim();
    
    // 파장 정보 추출 (430nm, 540nm 등)
    const wavelengthMatch = h.match(/\((\d+nm)\)/);
    if (wavelengthMatch) {
      const wavelength = wavelengthMatch[1];
      
      if (!wavelengthPatterns[wavelength]) {
        wavelengthPatterns[wavelength] = {};
      }
      
      // 좌표 위치 확인
      if (h.includes('TL')) {
        wavelengthPatterns[wavelength].TL = index;
      } else if (h.includes('TR')) {
        wavelengthPatterns[wavelength].TR = index;
      } else if (h.includes('BR')) {
        wavelengthPatterns[wavelength].BR = index;
      } else if (h.includes('BL')) {
        wavelengthPatterns[wavelength].BL = index;
      }
    }
  });

  // 각 파장별로 edgePoint 생성
  Object.keys(wavelengthPatterns).forEach(wavelength => {
    const positions = wavelengthPatterns[wavelength];
    
    // 모든 좌표가 있는 경우에만 추가
    if (positions.TL !== undefined && positions.TR !== undefined && 
        positions.BR !== undefined && positions.BL !== undefined) {
      
      edgePoints[`TL (${wavelength})`] = parseCoordinate(row[positions.TL]);
      edgePoints[`TR (${wavelength})`] = parseCoordinate(row[positions.TR]);
      edgePoints[`BR (${wavelength})`] = parseCoordinate(row[positions.BR]);
      edgePoints[`BL (${wavelength})`] = parseCoordinate(row[positions.BL]);
    }
  });

  return edgePoints;
};

/**
 * 좌표 문자열을 튜플로 변환
 */
const parseCoordinate = (coord) => {
  if (!coord) return [0, 0];
  
  const coordStr = String(coord).trim();
  const match = coordStr.match(/\((\d+),\s*(\d+)\)/);
  
  if (match) {
    return [parseInt(match[1]), parseInt(match[2])];
  }
  
  return [0, 0];
};

/**
 * 딥에이징 값을 seqno로 파싱 (NO=0, YES=1)
 */
const parseDeepAging = (value) => {
  if (!value) return 0;
  const str = String(value).trim().toUpperCase();
  return str === 'YES' || str === 'Y' || str === 'TRUE' || str === '1' ? 1 : 0;
};

/**
 * 날짜 형식 변환 (Excel 시리얼 번호 -> YYYY-MM-DD)
 */
const formatDate = (dateValue) => {
  if (!dateValue) return "";
  
  // 숫자인 경우 (Excel 시리얼 번호)
  if (typeof dateValue === 'number') {
    const excelBaseDate = new Date(1900, 0, 1);
    const resultDate = new Date(excelBaseDate.getTime() + (dateValue - 1) * 24 * 60 * 60 * 1000);
    return resultDate.toISOString().split('T')[0];
  }
  
  // 문자열인 경우
  const dateStr = String(dateValue).trim();
  if (dateStr.includes('-')) {
    return dateStr.split(' ')[0]; // 시간 부분 제거
  }
  
  return dateStr;
};

/**
 * 촬영일자에서 날짜 부분만 추출
 */
const parsePicturedDate = (value) => {
  if (!value) return "";
  
  const str = String(value).trim();
  // "2025-08-18 (Day7)" 형식에서 날짜만 추출
  const dateMatch = str.match(/(\d{4}-\d{2}-\d{2})/);
  return dateMatch ? dateMatch[1] : str;
};

/**
 * 기간 정보 추출 (Day7 등)
 */
const extractPeriod = (value) => {
  if (!value) return "";
  
  const str = String(value).trim();
  const periodMatch = str.match(/\((Day\d+)\)/i);
  return periodMatch ? periodMatch[1] : "";
};

/**
 * 촬영일자에서 isRefrigerated 판단 (Day1 = false, Day7 = true)
 */
const parseIsRefrigerated = (value) => {
  if (!value) return false;
  
  const str = String(value).trim();
  
  // Day1이 포함되어 있으면 false (냉장 안됨)
  if (str.includes('Day1')) {
    return false;
  }
  
  // Day7이 포함되어 있으면 true (냉장됨)
  if (str.includes('Day7')) {
    return true;
  }
  
  // 기본값은 false
  return false;
};


/**
 * 부위를 숫자 categoryId로 매핑하는 함수
 * @param {string} part - 부위명 (예: "s1", "S1", "목심" 등)
 * @returns {number} - categoryId (숫자)
 */
const mapPartToCategoryId = (part) => {
  if (!part) return 0;
  
  const partStr = String(part).trim().toLowerCase();
  
  // 샘플번호 패턴 (s1, s2, s3 등)
  const sampleMatch = partStr.match(/^s(\d+)$/);
  if (sampleMatch) {
    return parseInt(sampleMatch[1]) - 1; // s1 -> 0, s2 -> 1, s3 -> 2
  }
  
  // 기타 부위명은 숫자로 변환 시도, 실패 시 0
  const numValue = parseInt(partStr);
  return isNaN(numValue) ? 0 : numValue;
};

/**
 * 파장별 bands 데이터 추출 (RGB 제외, HSI만)
 * @param {Array} row - 데이터 행
 * @param {Object} headerMap - 헤더 매핑
 * @param {Array} headers - 전체 헤더 배열
 * @returns {Array} - bands 배열
 */
const extractBands = (row, headerMap, headers) => {
  const bands = [];
  const wavelengthData = {};
  
  // 파장별 좌표 패턴 찾기 (RGB 제외)
  headers.forEach((header, index) => {
    const h = String(header).trim();
    
    // 파장 정보 추출 (430nm, 540nm 등 - RGB 제외)
    const wavelengthMatch = h.match(/\((\d+nm)\)/);
    if (wavelengthMatch) {
      const wavelength = wavelengthMatch[1];
      
      if (!wavelengthData[wavelength]) {
        wavelengthData[wavelength] = {};
      }
      
      // 좌표 위치 확인
      if (h.includes('TL')) {
        wavelengthData[wavelength].topLeft = parseCoordinate(row[index]);
      } else if (h.includes('TR')) {
        wavelengthData[wavelength].topRight = parseCoordinate(row[index]);
      } else if (h.includes('BR')) {
        wavelengthData[wavelength].bottomRight = parseCoordinate(row[index]);
      } else if (h.includes('BL')) {
        wavelengthData[wavelength].bottomLeft = parseCoordinate(row[index]);
      }
    }
  });
  
  // 파장별로 bands 생성 (파장 순서대로 정렬)
  const sortedWavelengths = Object.keys(wavelengthData).sort((a, b) => {
    const numA = parseInt(a.replace('nm', ''));
    const numB = parseInt(b.replace('nm', ''));
    return numA - numB;
  });
  
  sortedWavelengths.forEach((wavelength, index) => {
    const positions = wavelengthData[wavelength];
    
    // 모든 좌표가 있는 경우에만 추가
    if (positions.topLeft && positions.topRight && 
        positions.bottomRight && positions.bottomLeft) {
      
      bands.push({
        spectral_index: index, // 0부터 시작
        topLeft: positions.topLeft,
        topRight: positions.topRight,
        bottomRight: positions.bottomRight,
        bottomLeft: positions.bottomLeft,
        filename: `${wavelength}.jpg` // 임시 파일명 (나중에 해싱된 이름으로 교체됨)
      });
    }
  });
  
  return bands;
};

/**
 * 여러 샘플을 각각 완전한 meat 객체로 그룹화
 * @param {Array} jsonArray - 개별 샘플 JSON 배열
 * @returns {Object} - 그룹화된 JSON (각 샘플별로 완전한 meat 객체)
 */
export const groupSamplesByTrace = (jsonArray) => {
  const grouped = {};
  
  jsonArray.forEach(item => {
    const traceNum = item.meat.traceNum;
    
    if (!grouped[traceNum]) {
      // 기본 구조 생성
      grouped[traceNum] = {
        userId: item.userId,
        rowId: `sheet1-${traceNum}`,
        traceNum: item.meat.traceNum,
        butcheryDate: item.meat.butcheryDate,
        manufactureDate: item.meat.manufactureDate,
        picturedDate: item.meat.picturedDate,
        period: item.meat.period,
        expirationDate: item.meat.expirationDate,
        hsi: item.meat.hsi,
        meat: [] // 각 샘플별 완전한 meat 객체 배열
      };
    }
    
    // 각 샘플의 완전한 meat 객체 추가
    grouped[traceNum].meat.push({
      sampleNum: item.meat.sampleNum,
      part: item.meat.part,
      gradeNum: item.meat.gradeNum,
      isDeepAging: item.meat.isDeepAging,
      marbling: item.meat.marbling,
      meatColor: item.meat.meatColor,
      texture: item.meat.texture,
      surfaceMoisture: item.meat.surfaceMoisture,
      total: item.meat.total,
      edgePoint: item.meat.edgePoint
    });
  });
  
  return Object.values(grouped);
};

/**
 * 이력번호별로 하나의 JSON 파일 생성을 위한 함수 (data_list 형식)
 * @param {Array} jsonArray - 개별 샘플 JSON 배열
 * @returns {Array} - 이력번호별 JSON 객체 배열
 */
export const createIndividualSampleJsons = (jsonArray) => {
  const groupedByTrace = {};
  
  // 이력번호별로 샘플들을 그룹화
  jsonArray.forEach(item => {
    const traceNum = item.traceNum;
    
    if (!groupedByTrace[traceNum]) {
      groupedByTrace[traceNum] = [];
    }
    
    // 원본 seqno 값을 유지 (딥에이징 컬럼에서 파싱된 값)
    const dataItem = {
      userId: item.userId,
      id: item.id,
      traceNum: item.traceNum,
      butcheryYmd: item.butcheryYmd,
      manufactureYmd: item.manufactureYmd,
      filmedAt: item.filmedAt,
      expireYmd: item.expireYmd,
      isRefrigerated: item.isRefrigerated,
      meat: {
        categoryId: item.meat.categoryId,
        gradeNum: item.meat.gradeNum,
        seqno: item.meat.seqno,
        marbling: item.meat.marbling,
        meat_color: item.meat.meat_color,
        texture: item.meat.texture,
        surface_moisture: item.meat.surface_moisture,
        overall: item.meat.overall,
        bands: item.meat.bands
      }
    };
    
    groupedByTrace[traceNum].push(dataItem);
  });
  
  // 이력번호별로 하나의 JSON 파일 생성
  const resultJsons = [];
  
  Object.keys(groupedByTrace).forEach(traceNum => {
    const dataList = groupedByTrace[traceNum];
    
    const jsonStructure = {
      data_list: dataList
    };
    
    resultJsons.push({
      fileName: `${traceNum}.json`,
      traceNum: traceNum,
      data: jsonStructure
    });
  });
  
  return resultJsons;
};

export default { convertExcelToJson, groupSamplesByTrace, createIndividualSampleJsons };