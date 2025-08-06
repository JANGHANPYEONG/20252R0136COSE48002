// src/api/fetchFilteredData.js

import { apiIP } from '../config';

export const fetchFilteredData = async (filters, type) => {
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
