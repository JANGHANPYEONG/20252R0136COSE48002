// Importing the useSWR hook from the "swr" library
import useSWR from 'swr';
import { apiIP } from '../../config';
import fetcher from '../fetcher';

//custom Hook인 getMeatListSWR를 export
export const useMeatList = (offset, count, startDate, endDate, specieValue) => {
  //육류 데이터 리스트를 API 서버로 부터 fetch
  const { data, error } = useSWR(
    //query parameter : offset, count, startDate, endDate
    `http://${apiIP}/meat/get?offset=${offset}&count=${count}&start=${startDate}&end=${endDate}&specieValue=${specieValue}`,
    //fetcher 함수 사용
    fetcher
  );

  //fetched data, loading state, error를 포함한 object 반환
  return {
    data,
    isLoading: !error && !data,
    error,
  };
};
