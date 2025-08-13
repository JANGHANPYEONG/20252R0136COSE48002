// src/api/predictData.js

import { apiIP } from '../config'; // 백엔드 ML 서버 주소

export const fetchPrediction = async (selectedRows) => {
  // dummy data
  const dummy = {
    'L01709271277001': {
        '색상(Color)': 7.0,
        '향(Aroma)': 6.5,
        '조직감(Texture)': 7.0,
        '즙성(Juiciness)': 6.2,
        '풍미(Flavor)': 6.8,
        '전체 기호도': 6.9,
    },
    'L01709271277002': {
        '색상(Color)': 7.5,
        '향(Aroma)': 5.5,
        '조직감(Texture)': 6.4,
        '즙성(Juiciness)': 7.7,
        '풍미(Flavor)': 9.1,
        '전체 기호도': 8.0,
    },
    'L01709271277003': {
        '색상(Color)': 8.0,
        '향(Aroma)': 7.0,
        '조직감(Texture)': 6.9,
        '즙성(Juiciness)': 6.5,
        '풍미(Flavor)': 7.2,
        '전체 기호도': 7.4,
    },
    'L01709271277004': {
        '색상(Color)': 7.2,
        '향(Aroma)': 6.6,
        '조직감(Texture)': 7.1,
        '즙성(Juiciness)': 6.8,
        '풍미(Flavor)': 7.0,
        '전체 기호도': 7.1,
    },
    'L01709271277005': {
        '색상(Color)': 7.4,
        '향(Aroma)': 6.9,
        '조직감(Texture)': 6.7,
        '즙성(Juiciness)': 6.4,
        '풍미(Flavor)': 6.8,
        '전체 기호도': 7.0,
    },
    'L01709271277006': {
        '색상(Color)': 7.3,
        '향(Aroma)': 6.7,
        '조직감(Texture)': 6.8,
        '즙성(Juiciness)': 6.9,
        '풍미(Flavor)': 7.1,
        '전체 기호도': 7.2,
    },
    'L01709271277007': {
        '색상(Color)': 7.6,
        '향(Aroma)': 6.8,
        '조직감(Texture)': 6.9,
        '즙성(Juiciness)': 6.6,
        '풍미(Flavor)': 7.0,
        '전체 기호도': 7.1,
    },
    'L01709271277008': {
        '색상(Color)': 7.9,
        '향(Aroma)': 7.0,
        '조직감(Texture)': 7.0,
        '즙성(Juiciness)': 6.7,
        '풍미(Flavor)': 7.1,
        '전체 기호도': 7.3,
    },
    'L01709271277009': {
        '색상(Color)': 7.5,
        '향(Aroma)': 6.4,
        '조직감(Texture)': 6.8,
        '즙성(Juiciness)': 6.6,
        '풍미(Flavor)': 6.9,
        '전체 기호도': 7.0,
    },
    'L01709271277010': {
        '색상(Color)': 7.8,
        '향(Aroma)': 6.9,
        '조직감(Texture)': 7.2,
        '즙성(Juiciness)': 6.8,
        '풍미(Flavor)': 7.2,
        '전체 기호도': 7.3,
    }
}



  // 목업용 dummy data return
  return dummy;
  try {
    const ids = selectedRows.map((item) => item.id);

    const response = await fetch(`http://${apiIP}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ data_ids: ids }),
    });

    if (!response.ok) {
      throw new Error('ML 서버 예측 요청 실패');
    }

    const result = await response.json();
    // 실제로는 result를 받아야함
    return result;
  } catch (err) {
    console.error('예측 API 실패:', err);
    throw err;
  }
};
