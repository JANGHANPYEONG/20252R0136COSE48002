// Importing the useSWR hook from the "swr" library
import useSWR from 'swr';
import { apiIP } from '../../config';
import fetcher from '../fetcher';

//custom Hook인 getPredictedMeatListSWR를 export
export const usePredictedMeatList = (
  offset,
  count,
  startDate,
  endDate,
  specieValue
) => {
  const { data, error } = useSWR(
    //query parameter : offset, count, startDate, endDate
    `http://${apiIP}/meat/get?offset=${offset}&count=${count}&start=${startDate}&end=${endDate}&specieValue=${specieValue}`,
    fetcher
  );

  //fetched data, loading state, error를 포함한 object 반환
  return {
    data,
    isLoading: !error && !data,
    error,
  };
};
export default usePredictedMeatList;
