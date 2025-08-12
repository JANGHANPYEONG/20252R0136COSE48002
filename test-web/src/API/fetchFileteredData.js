// src/api/fetchFilteredData.js
// filters나 type이 누락될 경우 대비 방어 코드 필요
// 응답 포맷 확인 로그 추가(디버깅용) 필요
// JS -> TS 필요
import { apiIP } from '../config';

export const fetchFilteredData = async (filters, type) => {
  // dummy data
      const dummy = [
      {
        id: 'M001',
        timestamp: '2025-08-07T10:15:00',
        date: '2025-08-07',
        spectrum: '...',
        wavelength: '650nm',
        sensory: {
          '색상': 7.0,
          '향(Aroma)': 6.5,
          '조직감(Texture)': 7.0,
          '즙성(Juiciness)': 6.2,
          '풍미(Flavor)': 6.8,
          '전체 기호도': 6.9,
        },
      },
      {
        id: 'M002',
        timestamp: '2025-08-07T10:15:00',
        date: '2025-08-07',
        spectrum: '...',
        wavelength: '650nm',
        sensory: {
          '색상': 7.5,
          '향(Aroma)': 5.5,
          '조직감(Texture)': 6.4,
          '즙성(Juiciness)': 7.7,
          '풍미(Flavor)': 9.1,
          '전체 기호도': 8.0,
        },
      },
      {
        id: 'M003',
        timestamp: '2025-08-07T11:20:00',
        date: '2025-08-07',
        spectrum: '...',
        wavelength: '660nm',
        sensory: {
          '색상': 8.0,
          '향(Aroma)': 7.0,
          '조직감(Texture)': 6.9,
          '즙성(Juiciness)': 6.5,
          '풍미(Flavor)': 7.2,
          '전체 기호도': 7.4,
        },
      },
    ];
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
