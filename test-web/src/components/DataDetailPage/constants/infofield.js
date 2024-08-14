export const apiField = [
  'birthYmd',
  'butcheryYmd',
  'farmAddr',
  'farmerName',
  'gradeNm',
  'primalValue',
  'secondaryValue',
  'sexType',
  'species',
  'statusType',
  'traceNum',
];

export const apiDBFieldToSemanticWord = {
  birthYmd: '출생년월일',
  butcheryYmd: '도축일자',
  farmAddr: '사육지',
  farmerName: '소유주',
  gradeNm: '육질등급',
  primalValue: '대분류',
  secondaryValue: '소분류',
  sexType: '성별',
  species: '종',
  statusType: '데이터승인',
  traceNum: 'traceNum',
};

export const heatedField = [
  'flavor',
  'juiciness',
  'umami',
  'palatability',
  'tenderness0',
  'tenderness3',
  'tenderness7',
  'tenderness14',
  'tenderness21',
];

export const heatedDBFieldToSemanticWord = {
  flavor: '풍미',
  juiciness: '육즙',
  umami: '감칠맛',
  palatability: '기호도',
  tenderness0: '연도(0)',
  tenderness3: '연도(3)',
  tenderness7: '연도(7)',
  tenderness14: '연도(14)',
  tenderness21: '연도(21)',
};

export const heatedStaticField = [
  'flavor',
  'juiciness',
  'tenderness',
  'umami',
  'palatability',
];

export const heatedStaticDBFieldToSemanticWord = {
  flavor: '풍미',
  juiciness: '육즙',
  tenderness: '연도',
  umami: '감칠맛',
  palatability: '기호도',
};

export const labField = [
  'L',
  'a',
  'b',
  'DL',
  'CL',
  'RW',
  'ph',
  'WBSF',
  'cardepsin_activity',
  'MFI',
  'sourness',
  'bitterness',
  'umami',
  'richness',
  'Collagen',
];

export const labDBFieldToSemanticWord = {
  L: '명도',
  a: '적색도',
  b: '황색도',
  DL: '육즙감량',
  CL: '가열감량',
  RW: '압착감량',
  ph: 'pH',
  WBSF: '전단가',
  cardepsin_activity: '카뎁신활성도',
  MFI: '근소편화지수',
  sourness: '신맛',
  bitterness: '진한맛',
  umami: '감칠맛',
  richness: '후미',
  Collagen: '콜라겐',
};

export const labStaticField = [
  'L',
  'a',
  'b',
  'DL',
  'CL',
  'RW',
  'ph',
  'WBSF',
  'cardepsin_activity',
  'MFI',
  'sourness',
  'bitterness',
  'umami',
  'richness',
  'Collagen',
];

export const labStaticDBFieldToSemanticWord = {
  L: '명도',
  a: '적색도',
  b: '황색도',
  DL: '육즙감량',
  CL: '가열감량',
  RW: '압착감량',
  ph: 'pH',
  WBSF: '전단가',
  cardepsin_activity: '카뎁신활성도',
  MFI: '근소편화지수',
  sourness: '신만',
  bitterness: '진한맛',
  umami: '감칠맛',
  richness: '후미',
  collagen: '콜라겐',
};

export const rawField = [
  'marbling',
  'color',
  'texture',
  'surfaceMoisture',
  'overall',
];

export const rawDBFieldToSematicWord = {
  marbling: '마블링',
  color: '육색',
  texture: '조직감',
  surfaceMoisture: '표면육즙',
  overall: '기호도',
};

export const deepAgingField = [
  'marbling',
  'color',
  'texture',
  'surfaceMoisture',
  'overall',
  'createdAt',
  //'seqno',
  'minute',
  'period',
];

export const deepAgingDBFieldToSemanticWord = {
  marbling: '마블링',
  color: '육색',
  texture: '조직감',
  surfaceMoisture: '표면육즙',
  overall: '기호도',
  createdAt: '생성일자',
  //seqno: '딥에이징 회차',
  minute: '딥에이징 시간(분)',
  period: 'period',
};

export const deepAgingStaticField = [
  'marbling',
  'color',
  'texture',
  'surfaceMoisture',
  'overall',
];

export const deepAgingStaticDBFieldToSemanticWord = {
  marbling: '마블링',
  color: '육색',
  texture: '조직감',
  surfaceMoisture: '표면육즙',
  overall: '기호도',
};

export const rawPAField = [
  'marbling',
  'color',
  'texture',
  'surfaceMoisture',
  'overall',
  'xai_gradeNum',
];

export const rawPADBFieldToSematicWord = {
  marbling: '마블링',
  color: '육색',
  texture: '조직감',
  surfaceMoisture: '표면육즙',
  overall: '기호도',
  xai_gradeNum: '예상등급',
};

export const deepAgingPAField = [
  'marbling',
  'color',
  'texture',
  'surfaceMoisture',
  'overall',
  'xai_gradeNum',
];

export const deepAgingPADBFieldToSemanticWord = {
  marbling: '마블링',
  color: '육색',
  texture: '조직감',
  surfaceMoisture: '표면육즙',
  overall: '기호도',
  xai_gradeNum: '예상등급',
};
