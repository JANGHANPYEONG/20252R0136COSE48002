import { useParams, useLocation, Link } from 'react-router-dom';
import { Box, IconButton } from '@mui/material';
import 'bootstrap/dist/css/bootstrap.css';
import { FaArrowLeft } from 'react-icons/fa';
import DataLoad from '../components/DataDetailPage/DetailDataController';

const navy = '#0F3659';

function DataEdit() {
  // 쿼리스트링 추출
  const searchParams = useLocation().search;
  const pageOffset = new URLSearchParams(searchParams).get('pageOffset');
  const startDate = new URLSearchParams(searchParams).get('startDate');
  const endDate = new URLSearchParams(searchParams).get('endDate');
  console.log('수정 및 조회', { pageOffset, startDate, endDate });

  //관리번호
  const idParam = useParams();

  return (
    <Box style={{ width: '100%', padding: '0px 80px' }}>
      <Box>
        {/**데이터 목록으로 돌아가기 위한 컴포넌트 */}
        <div style={style.fixed}>
          <Link
            to={{
              pathname: '/DataManage',
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
          </Link>
        </div>
      </Box>
      {/**상세 조회 데이터 fetch */}
      <DataLoad id={idParam.id} page={'수정및조회'} />
    </Box>
  );
}
export default DataEdit;

const style = {
  fixed: {
    marginTop: '80px',
    right: '0',
    left: '80px',
    zIndex: 1,
    width: 'fit-content',
    borderRadius: '0',
    display: 'flex',
    justifyContent: 'space-between',
    height: '70px',
  },
};
