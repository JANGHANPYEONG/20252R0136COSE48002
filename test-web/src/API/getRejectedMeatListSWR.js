// Importing the useSWR hook from the "swr" library
import useSWR from 'swr';
import { apiIP } from '../config';

// data fetching을 위한 함수(fetcher)
const fetcher = (...args) =>
  fetch(...args).then((res) => {
    switch (res.status) {
      //response status가 200 (OK)인 경우, JSON을 파싱한 후 data 반환
      case 200:
        return res.json();
      //response status가 404 (Not Found)인 경우, 에러 throw
      case 404:
        throw new Error('No Rejected Datas Found');
      //그 외 response status의 경우, JSON을 파싱한 후 data 반환
      default:
        return res.json();
    }
  });

//custom Hook인 useRejectedMeatListFetch를 export
export const useRejectedMeatListFetch = (offset, count, startDate, endDate) => {
  //육류 반려 데이터 리스트를 API 서버로 부터 fetch
  const { data, error } = useSWR(
    //query parameter : offset, count, startDate, endDate
    `http://${apiIP}/meat/get/by-status-range?statusType=1&offset=${offset}&count=${count}&start=${startDate}&end=${endDate}`,
    fetcher
  );

  //fetched data, loading state, error를 포함한 object 반환
  return {
    data,
    isLoading: !error && !data,
    error,
  };
};
