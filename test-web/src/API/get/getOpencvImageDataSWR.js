// Importing the useSWR hook from the "swr" library
import useSWR from 'swr';
import { apiIP } from '../../config';
import fetcher from '../fetcher';

export const useOpencvImageData = (meatId) => {
  //id에 대항하는 육류 상세 데이터를 AmI 서버로 부터 fetch
  const { data, error } = useSWR(
    //query parameter : id
    `http://${apiIP}/meat/get/opencv-image?meatId=${meatId}`,
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
export default useOpencvImageData;
