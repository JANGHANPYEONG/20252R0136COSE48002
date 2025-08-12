// src/api/predictData.js

import { apiIP } from '../config'; // 백엔드 ML 서버 주소

export const fetchPrediction = async (selectedRows) => {
  // dummy data
  const dummy = {
    M001: {
      '색상': 7.2,
      '향(Aroma)': 6.8,
      '조직감(Texture)': 6.9,
      '즙성(Juiciness)': 6.5,
      '풍미(Flavor)': 7.1,
      '전체 기호도': 7.0,
    },
    M002: {
      '색상': 7.8,
      '향(Aroma)': 5.8,
      '조직감(Texture)': 6.6,
      '즙성(Juiciness)': 7.9,
      '풍미(Flavor)': 9.3,
      '전체 기호도': 8.2,
    },
    M003: {
      '색상': 8.1,
      '향(Aroma)': 7.4,
      '조직감(Texture)': 7.0,
      '즙성(Juiciness)': 6.8,
      '풍미(Flavor)': 7.5,
      '전체 기호도': 7.6,
    },
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
