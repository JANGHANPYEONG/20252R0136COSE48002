// src/api/predict.js
// 선택된 분광 데이터 예측 모델로 전송

import apiIP from '../config';

export const fetchPrediction = async (selectedIds) => {
  const response = await fetch(`http://${apiIP}/data/filter`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ids: selectedIds }),
  });

  if (!response.ok) {
    throw new Error('예측 요청 실패');
  }

  const result = await response.json(); // { id: 예측결과 } 형태 예상
  return result;
};
