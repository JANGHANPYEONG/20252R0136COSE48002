// Script to generate a corrected JSON with proper filename mapping
const fs = require('fs');
const { saveJsonToResult } = require('./src/API/add/saveJsonToResult.js');

async function generateCorrectedJson() {
  try {
    console.log('=== 이전 JSON (filename 매핑 전) ===');
    const existingJson = JSON.parse(fs.readFileSync('test-data/result/140119100857.json', 'utf8'));
    console.log('첫 번째 샘플의 bands:');
    console.log(JSON.stringify(existingJson.data_list[0].meat.bands, null, 2));
    
    // 이미 수정된 saveJsonToResult 함수를 사용해서 새 JSON 생성
    // 실제 Excel 파일과 ZIP 파일을 가짜 데이터와 함께 사용
    const excelFile = { name: '140119100857.xlsx' }; // 임시 객체
    const zipFile = fs.readFileSync('test-data/msi/140119100857 root/140119100857.zip');
    
    // 기존 데이터를 테이블 형태로 변환 (saveJsonToResult 함수 파라미터에 맞춤)
    const tableData = existingJson.data_list.map((item, index) => ({
      '이력번호': item.traceNum,
      '샘플번호': index + 1,
      '샘플_번호': index + 1,
      // 기타 필요한 데이터들을 기존 JSON에서 추출
      '대분할': item.meat.categoryId === 0 ? '등심' : '기타',
      '등급': item.meat.gradeNum || 'X',
      '마블링': item.meat.marbling,
      '육색': item.meat.meat_color,
      '조직감': item.meat.texture,
      '표면수분': item.meat.surface_moisture,
      '종합': item.meat.overall,
      '도축일자': item.butcheryYmd,
      '제조일자': item.manufactureYmd,
      '촬영일자': item.filmedAt,
      '유통기한': item.expireYmd
    }));
    
    console.log('\n=== saveJsonToResult 함수로 올바른 filename 매핑 테스트 중... ===');
    
    // Mock the convertExcelToJson function for testing
    const originalFunction = require('./src/API/add/excelToJsonConverter.js').convertExcelToJson;
    
    // Create a simple mock result that mimics the Excel conversion
    const mockJsonArray = existingJson.data_list.map((item, index) => ({
      traceNum: item.traceNum,
      sampleNumber: index + 1,
      part: '등심',
      grade: item.meat.gradeNum || 'X',
      marbling: item.meat.marbling,
      meat_color: item.meat.meat_color,
      texture: item.meat.texture,
      surface_moisture: item.meat.surface_moisture,
      overall: item.meat.overall,
      butcheryYmd: item.butcheryYmd,
      manufactureYmd: item.manufactureYmd,
      filmedAt: item.filmedAt,
      expireYmd: item.expireYmd,
      bands: item.meat.bands.map(band => ({
        ...band,
        filename: band.filename // 이 부분이 매핑으로 교체될 예정
      }))
    }));
    
    // 매핑 함수만 테스트하기 위해 간단한 개별 JSON 생성
    const { createIndividualSampleJsons } = require('./src/API/add/excelToJsonConverter.js');
    const individualJsons = createIndividualSampleJsons(mockJsonArray);
    
    console.log('개별 JSON 생성 완료:', individualJsons.length, '개');
    
    // 매핑 함수 직접 호출
    const { mapImageFilenamesToJsons } = require('./src/API/add/saveJsonToResult.js');
    const mappedJsons = await mapImageFilenamesToJsons(individualJsons, zipFile);
    
    console.log('\n=== 수정된 JSON (filename 매핑 후) ===');
    console.log('첫 번째 샘플의 bands:');
    console.log(JSON.stringify(mappedJsons[0].data.data_list[0].meat.bands, null, 2));
    
    console.log('\n두 번째 샘플의 bands:');
    console.log(JSON.stringify(mappedJsons[0].data.data_list[1].meat.bands, null, 2));
    
    // 수정된 JSON을 새 파일로 저장
    const correctedJson = mappedJsons[0].data;
    fs.writeFileSync('test-data/result/140119100857_corrected.json', JSON.stringify(correctedJson, null, 2));
    console.log('\n✅ 수정된 JSON이 140119100857_corrected.json으로 저장되었습니다.');
    
  } catch (error) {
    console.error('오류 발생:', error);
  }
}

generateCorrectedJson().catch(console.error);