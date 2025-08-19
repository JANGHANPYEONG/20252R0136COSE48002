// src/api/fetchFilteredData.js
// filters나 type이 누락될 경우 대비 방어 코드 필요
// 응답 포맷 확인 로그 추가(디버깅용) 필요
// JS -> TS 필요
import { apiIP } from '../config';

export const fetchFilteredData = async (filters, type) => {
  // 필터 객체에서 dataType 가져오기
  const dataTypeFilter = filters.find(f => f.name === '데이터 타입');
  const dataType = dataTypeFilter?.value || null;
  
  // dummy data
  let dummy = [
  {
    id: 'L01709271277001',
    sampleNo: 'S001',
    part: '등심',
    deepAging: 'Y',
    slDate: '2025-08-07',
    timestamp: '2025-08-07T10:15:00',
    admit: 'N',
    sensory: {
      '색상(Color)': 6.9,
      '향(Aroma)': 6.6,
      '조직감(Texture)': 7.1,
      '즙성(Juiciness)': 6.3,
      '풍미(Flavor)': 6.7,
      '전체 기호도': 6.8,
    },
    spectral: {
  MSI: {
    '0': {
      wavelengths: [450, 460, 470, 480, 490, 500, 510, 520],
      values:      [0.12, 0.14, 0.18, 0.22, 0.25, 0.27, 0.29, 0.30],
    },
    '7': {
      wavelengths: [450, 460, 470, 480, 490, 500, 510, 520],
      values:      [0.10, 0.13, 0.17, 0.21, 0.23, 0.26, 0.28, 0.29],
    },
  },
  RGB: {
    '0': {
      wavelengths: [450, 460, 470, 480, 490, 500, 510, 520],
      values:      [0.08, 0.09, 0.11, 0.15, 0.18, 0.19, 0.20, 0.21],
    },
    '7': {
      wavelengths: [450, 460, 470, 480, 490, 500, 510, 520],
      values:      [0.09, 0.10, 0.12, 0.16, 0.17, 0.18, 0.19, 0.20],
    },
  },
},
  },
  {
    id: 'L01709271277002',
    sampleNo: 'S002',
    part: '안심',
    deepAging: 'N',
    slDate: '2025-08-07',
    timestamp: '2025-08-07T10:15:00',
    admit: 'Y',
    sensory: {
      '색상(Color)': 7.6,
      '향(Aroma)': 5.7,
      '조직감(Texture)': 6.5,
      '즙성(Juiciness)': 7.8,
      '풍미(Flavor)': 9.0,
      '전체 기호도': 8.1,
    },
  },
  {
    id: 'L01709271277003',
    sampleNo: 'S003',
    part: '갈비',
    deepAging: 'Y',
    slDate: '2025-08-07',
    timestamp: '2025-08-07T11:20:00',
    admit: 'Y',
    sensory: {
      '색상(Color)': 8.2,
      '향(Aroma)': 6.9,
      '조직감(Texture)': 7.1,
      '즙성(Juiciness)': 6.6,
      '풍미(Flavor)': 7.1,
      '전체 기호도': 7.5,
    },
  },
  {
    id: 'L01709271277004',
    sampleNo: 'S004',
    part: '목심',
    deepAging: 'N',
    slDate: '2025-08-07',
    timestamp: '2025-08-07T11:20:00',
    admit: 'Y',
    sensory: {
      '색상(Color)': 7.1,
      '향(Aroma)': 6.5,
      '조직감(Texture)': 7.0,
      '즙성(Juiciness)': 6.9,
      '풍미(Flavor)': 7.1,
      '전체 기호도': 7.0,
    },
  },
  {
    id: 'L01709271277005',
    sampleNo: 'S005',
    part: '양지',
    deepAging: 'Y',
    slDate: '2025-08-07',
    timestamp: '2025-08-07T10:15:00',
    admit: 'Y',
    sensory: {
      '색상(Color)': 7.3,
      '향(Aroma)': 6.8,
      '조직감(Texture)': 6.6,
      '즙성(Juiciness)': 6.5,
      '풍미(Flavor)': 6.9,
      '전체 기호도': 7.1,
    },
  },
  {
    id: 'L01709271277006',
    sampleNo: 'S006',
    part: '채끝',
    deepAging: 'N',
    slDate: '2025-08-07',
    timestamp: '2025-08-07T11:20:00',
    admit: 'Y',
    sensory: {
      '색상(Color)': 7.4,
      '향(Aroma)': 6.8,
      '조직감(Texture)': 6.9,
      '즙성(Juiciness)': 7.0,
      '풍미(Flavor)': 7.0,
      '전체 기호도': 7.2,
    },
  },
  {
    id: 'L01709271277007',
    sampleNo: 'S007',
    part: '등심',
    deepAging: 'Y',
    slDate: '2025-08-07',
    timestamp: '2025-08-07T10:15:00',
    admit: 'Y',
    sensory: {
      '색상(Color)': 7.5,
      '향(Aroma)': 6.9,
      '조직감(Texture)': 7.0,
      '즙성(Juiciness)': 6.7,
      '풍미(Flavor)': 7.1,
      '전체 기호도': 7.0,
    },
  },
  {
    id: 'L01709271277008',
    sampleNo: 'S008',
    part: '안심',
    deepAging: 'Y',
    slDate: '2025-08-07',
    timestamp: '2025-08-07T11:20:00',
    admit: 'Y',
    sensory: {
      '색상(Color)': 7.8,
      '향(Aroma)': 7.1,
      '조직감(Texture)': 6.9,
      '즙성(Juiciness)': 6.8,
      '풍미(Flavor)': 7.0,
      '전체 기호도': 7.4,
    },
  },
  {
    id: 'L01709271277009',
    sampleNo: 'S009',
    part: '갈비',
    deepAging: 'N',
    slDate: '2025-08-07',
    timestamp: '2025-08-07T10:15:00',
    admit: 'Y',
    sensory: {
      '색상(Color)': 7.4,
      '향(Aroma)': 6.5,
      '조직감(Texture)': 6.9,
      '즙성(Juiciness)': 6.7,
      '풍미(Flavor)': 7.0,
      '전체 기호도': 7.1,
    },
  },
  {
    id: 'L01709271277010',
    sampleNo: 'S010',
    part: '목심',
    deepAging: 'Y',
    slDate: '2025-08-07',
    timestamp: '2025-08-07T11:20:00',
    admit: 'Y',
    sensory: {
      '색상(Color)': 7.7,
      '향(Aroma)': 7.0,
      '조직감(Texture)': 7.3,
      '즙성(Juiciness)': 6.9,
      '풍미(Flavor)': 7.3,
      '전체 기호도': 7.4,
    },
  },
];


  // 데이터 타입에 따라 필터링 (실제 API에서는 서버에서 처리됨)
  if (dataType === 'RGB') {
    // RGB 데이터만 표시 (짝수 ID 데이터를 RGB로 가정)
    dummy = dummy.filter(item => parseInt(item.id.slice(-2)) % 2 === 0);
  } else if (dataType === 'MSI') {
    // MSI 데이터만 표시 (홀수 ID 데이터를 MSI로 가정)
    dummy = dummy.filter(item => parseInt(item.id.slice(-2)) % 2 !== 0);
  }
  
  // 목업용 dummy data return
  return dummy;
  try {
    const response = await fetch(`http://${apiIP}/data/filter`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ filters, type }),
    });

    if (!response.ok) {
      throw new Error('서버 응답 오류');
    }

    const result = await response.json();
    return result.data; // 백엔드에서 { data: [...] } 형태로 응답된다고 가정
  } catch (error) {
    console.error('필터링된 데이터 요청 실패:', error);
    return [];
  }
};
