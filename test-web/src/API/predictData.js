// src/api/predictData.js

import { apiIP } from '../config'; // 백엔드 ML 서버 주소

export const fetchPrediction = async (selectedRows) => {
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
    return result;
  } catch (err) {
    console.error('예측 API 실패:', err);
    throw err;
  }
};
