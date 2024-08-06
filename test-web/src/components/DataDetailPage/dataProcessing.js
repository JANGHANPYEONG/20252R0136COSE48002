// 축산물 이력 데이터를 json 객체로 변환하는 함수
const convertToApiData = (
  birthYmd,
  butcheryYmd,
  company,
  createdAt,
  farmAddr,
  farmerName,
  gradeNum,
  imagePath,
  meatId,
  primalValue,
  secondaryValue,
  sexType,
  specieValue,
  statusType,
  traceNum,
  userId,
  userName,
  userType
) => {
  // JSON 객체
  const apiData = {
    birthYmd: birthYmd,
    butcheryYmd: butcheryYmd,
    company: company,
    createdAt: createdAt,
    farmAddr: farmAddr,
    farmerName: farmerName,
    gradeNm: gradeNum,
    imagePath: imagePath,
    meatId: meatId,
    primalValue: primalValue,
    secondaryValue: secondaryValue,
    sexType: sexType,
    species: specieValue,
    statusType: statusType,
    traceNum: traceNum,
    userId: userId,
    userName: userName,
    userType: userType,
  };
  console.log('apidata2 : ', apiData);
  return apiData;
};

// 데이터 전처리
const dataProcessing = (items) => {
  // 3-1. 축산물 이력 데이터 json 객체로 만들기
  const apiData = convertToApiData(
    items.birthYmd,
    items.butcheryYmd,
    items.company,
    items.createdAt,
    items.farmAddr,
    items.farmerName,
    items.gradeNum,
    items.imagePath,
    items.meatId,
    items.primalValue,
    items.secondaryValue,
    items.sexType,
    items.specieValue,
    items.statusType,
    items.traceNum,
    items.userId,
    items.userName,
    items.userType
  );
  // Check if deepAgingInfo exists and is an array
  const deepAgingInfo = Array.isArray(items.deepAgingInfo)
    ? items.deepAgingInfo
    : [];

  // 3-2. 처리육이 있는 경우 가열육, 실험실 추가 데이터 필요 -> 배열로 관리 , 기본 값은 원육으로
  let processedData = [];
  let heatedData = [
    deepAgingInfo[0] ? deepAgingInfo[0].heatedmeat_sensory_eval || {} : {},
  ];
  let labData = [deepAgingInfo[0] ? deepAgingInfo[0].probexpt_data || {} : {}];
  let processedMinute = [];

  // 데이터 처리 횟수 parsing ex) 1회, 2회 ,...
  let processedDataSeq = ['원육'];
  // 처리육 이미지
  let processedDataImgPath = [];
  let processedDate=[];

  // n회차 처리육에 대한 회차별 정보
  for (let i = 1; i < deepAgingInfo.length; i++) {
    if (deepAgingInfo[i]) {
      processedDataSeq = [...processedDataSeq, `${i}회`];
      processedData = [...processedData, deepAgingInfo[i].sensory_eval || {}];
      heatedData = [
        ...heatedData,
        deepAgingInfo[i].heatedmeat_sensory_eval || {},
      ];
      labData = [...labData, deepAgingInfo[i].probexpt_data || {}];
      processedMinute = [...processedMinute, deepAgingInfo[i].minute || 0];
      processedDataImgPath = [
        ...processedDataImgPath,
        deepAgingInfo[i]?.sensory_eval?.imagePath || 'null',
      ];
      processedDate = [...processedDate, deepAgingInfo[i].date || {}];
    }
  }

  // 3-3. 데이터를 json 객체로 만들기
  const data = {
    meatId: items.meatId,
    userId: items.userId,
    createdAt: items.createdAt ? items.createdAt.replace('T', ' ') : '', // 수정 부분: 기본 값 설정
    qrImagePath: items.imagePath,
    raw_data: deepAgingInfo[0] ? deepAgingInfo[0].sensory_eval || {} : {},
    raw_img_path: deepAgingInfo[0]
      ? deepAgingInfo[0].sensory_eval?.imagePath || {}
      : {},
    processed_data: processedData,
    heated_data: heatedData,
    lab_data: labData,
    api_data: apiData,
    processed_data_seq: processedDataSeq,
    processed_minute: processedMinute,
    processed_img_path: processedDataImgPath,
    processed_date : processedDate
  };

  return data;
};
export default dataProcessing;
