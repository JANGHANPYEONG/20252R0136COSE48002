// Importing the useSWR hook from the "swr" library
import useSWR from 'swr';
import { apiIP } from '../../config';
import fetcher from '../fetcher';

//custom Hook인 statisticStackedBarSWR를 export
export const useStatisticStackedBar = (startDate, endDate) => {
  //stacked bar 데이터를 API 서버로 부터 fetch
  const { data, error } = useSWR(
    //query parameter : startDate, endDate
    `http://${apiIP}/meat/statistic/counts/by-large-part?start=${startDate}&end=${endDate}`,
    fetcher
  );

  //fetched data, loading state, error를 포함한 object 반환
  return {
    data,
    isLoading: !error && !data,
    isError: error,
  };
};
