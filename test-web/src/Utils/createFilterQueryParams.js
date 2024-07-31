import { useLocation } from 'react-router-dom';

const CreateFilterQueryParams = () => {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search); // 현재 쿼리 파라미터를 복사
  return queryParams.toString();
};

export default CreateFilterQueryParams;
