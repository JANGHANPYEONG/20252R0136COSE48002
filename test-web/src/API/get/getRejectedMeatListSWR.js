// Importing the useSWR hook from the "swr" library
import useSWR from 'swr';
import { apiIP } from '../../config';
import fetcher from '../fetcher';

//custom Hook인 getRejectedMeatListSWR를 export
export const useRejectedMeatList = (
  offset,
  count,
  startDate,
  endDate,
  specieValue
) => {
  //육류 반려 데이터 리스트를 API 서버로 부터 fetch
  const { data, error } = useSWR(
    //query parameter : offset, count, startDate, endDate
    `http://${apiIP}/meat/get/by-status?statusType=1&offset=${offset}&count=${count}&start=${startDate}&end=${endDate}&specieValue=${specieValue}`,
    fetcher
  );

  //fetched data, loading state, error를 포함한 object 반환
  return {
    data,
    isLoading: !error && !data,
    error,
  };
};

export default useRejectedMeatList;
