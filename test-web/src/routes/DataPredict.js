import { useParams, useLocation, Link } from 'react-router-dom';
import { Box, IconButton } from '@mui/material';
import 'bootstrap/dist/css/bootstrap.css';
import { FaArrowLeft } from 'react-icons/fa';
import DataLoad from '../components/DataDetailPage/DetailDataController';

const navy = '#0F3659';

const DataPredict = () => {
  //관리번호
  const idParam = useParams();
  // 쿼리스트링 추출
  const searchParams = useLocation().search;
  const pageOffset = new URLSearchParams(searchParams).get('pageOffset');
  const startDate = new URLSearchParams(searchParams).get('startDate');
  const endDate = new URLSearchParams(searchParams).get('endDate');
  console.log('예측', { pageOffset, startDate, endDate });

  return (
    <Box sx={{ width: '100%', height: '100%', padding: '80px 80px' }}>
      <Box>
        {/**데이터 목록으로 돌아가기 위한 컴포넌트 */}
        <div style={style.fixed}>
          <Link
            to={{
              pathname: '/PA',
              search: `?pageOffset=${pageOffset}&startDate=${startDate}&endDate=${endDate}`,
            }}
            style={{
              textDecorationLine: 'none',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <IconButton
              style={{
                color: `${navy}`,
                backgroundColor: 'white',
                border: `1px solid ${navy}`,
                borderRadius: '10px',
                marginRight: '10px',
              }}
            >
              <FaArrowLeft />
            </IconButton>
          </Link>
          <span
            style={{
              textDecoration: 'none',
              color: `${navy}`,
              fontSize: '30px',
              fontWeight: '600',
            }}
          >
            {idParam.id}
          </span>
        </div>
      </Box>
      {/**상세 조회 데이터 fetch */}
      <DataLoad id={idParam.id} page={'예측'} />
    </Box>
  );
};
export default DataPredict;

const style = {
  fixed: {
    //position: 'fixed',
    marginTop: '60px',
    right: '0',
    zIndex: 1,
    width: 'fit-content',
    borderRadius: '0',
    display: 'flex',
    justifyContent: 'space-between',
    //backgroundColor:'#F5F5F5',
    height: 'fit-content',
    alignItems: 'center',
  },
};
