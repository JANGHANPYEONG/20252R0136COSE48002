import { useQuery } from '@tanstack/react-query';
import { getMeatDetail } from './getMeatDetail';

export default function useMeatDetail(id, { enabled = true } = {}) {
  return useQuery({
    queryKey: ['meatDetail', id],
    queryFn: ({ signal }) => getMeatDetail(id, signal),
    enabled: !!id && enabled,
    staleTime: 60_000,
    retry: 1,
  });
}
