// src/api/fetchFilteredData.js
// 백엔드가 기대하는 필터 구조에 맞게 수정
import { apiIP } from '../config';

export const fetchFilteredData = async (filters) => {
  try {
    // 백엔드가 기대하는 필터 구조로 변환
    const backendFilters = {
      categoryIds: null, // 전체 선택 시 null
      butcheryYmd_from: null,
      butcheryYmd_to: null,
      createdAt_from: null,
      createdAt_to: null,
      page: 1,
      pageSize: 50
    };

    // 날짜 필터 처리
    const dateFilter = filters.find(f => f.name === '날짜');
    if (dateFilter && dateFilter.value) {
      if (dateFilter.value.start) {
        backendFilters.butcheryYmd_from = dateFilter.value.start;
        backendFilters.createdAt_from = `${dateFilter.value.start}T00:00:00`;
      }
      if (dateFilter.value.end) {
        backendFilters.butcheryYmd_to = dateFilter.value.value.end;
        backendFilters.createdAt_to = `${dateFilter.value.end}T23:59:59`;
      }
    }

    // 품종 필터 처리 (categoryIds)
    const specieFilter = filters.find(f => f.name === '품종');
    if (specieFilter && specieFilter.value && specieFilter.value !== '전체') {
      // 품종별 categoryIds 매핑
      const categoryMapping = {
        '소': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        '돼지': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        '닭': [30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
      };
      backendFilters.categoryIds = categoryMapping[specieFilter.value] || [];
    }

    // 페이지네이션 처리
    const pageFilter = filters.find(f => f.name === 'page');
    const pageSizeFilter = filters.find(f => f.name === 'pageSize');

    if (pageFilter) {
      backendFilters.page = pageFilter.value;
    }
    if (pageSizeFilter) {
      backendFilters.pageSize = pageSizeFilter.value;
    }

    // API 호출 (POST 방식으로 변경)
    const response = await fetch(`http://${apiIP}/dashboard/dashboard/bulk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendFilters),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    // 백엔드 응답 구조에 맞게 데이터 반환
    if (result && result.items) {
      return result.items;
    }

    return result || [];

  } catch (error) {
    console.error('필터링된 데이터 요청 실패:', error);

    // 에러 발생 시 빈 배열 반환
    return [];
  }
};
