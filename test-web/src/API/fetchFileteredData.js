// src/api/fetchFilteredData.js
// 백엔드가 기대하는 필터 구조에 맞게 수정
import { apiIP } from '../config';

export const fetchFilteredData = async (filters) => {
  try {
    let backendFilters;
    
    // 새로운 백엔드 필터 형식인지 확인
    if (filters.filters) {
      // 이미 올바른 형식으로 되어 있음
      backendFilters = filters.filters;
    } else {
      // 기존 형식에서 변환 (하위 호환성)
      backendFilters = {
        categoryIds: [], // 현재는 빈 배열로 설정 (필요시 추가)
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
          backendFilters.butcheryYmd_to = dateFilter.value.end;
          backendFilters.createdAt_to = `${dateFilter.value.end}T23:59:59`;
        }
      }

      // 품종 필터 처리 (categoryIds)
      const specieFilter = filters.find(f => f.name === '품종');
      if (specieFilter && specieFilter.categoryIds && specieFilter.categoryIds.length > 0) {
        backendFilters.categoryIds = specieFilter.categoryIds;
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
    }

    // API 호출 (POST 방식)
    const response = await fetch(`http://${apiIP}/data/filter`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ filters: backendFilters }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    // 백엔드 응답 구조에 맞게 데이터 반환
    if (result && result.data) {
      return result.data;
    }
    
    return result || [];
    
  } catch (error) {
    console.error('필터링된 데이터 요청 실패:', error);
    
    // 에러 발생 시 빈 배열 반환
    return [];
  }
};
