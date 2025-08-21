// src/Utils/useFileList.js
import { useQuery } from '@tanstack/react-query';
import { fetchFilteredData } from '../API/fetchFileteredData';

const buildKey = (filters) => {
  const date = filters?.find?.(f => f.name === '날짜')?.value || {};
  const dtype = filters?.find?.(f => f.name === '데이터 타입')?.value || null;
  const start = date?.start ?? null;
  const end   = date?.end   ?? null;
  return ['fileList', { start, end, dtype }];
};

export default function useFileList(filters, { enabled = true } = {}) {
  return useQuery({
    queryKey: buildKey(filters),
    queryFn: () => fetchFilteredData(filters),
    select: (data) => data ?? [],
    enabled, // ← 버튼으로 on/off
    refetchOnWindowFocus: false,
    staleTime: 5 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
  });
}
