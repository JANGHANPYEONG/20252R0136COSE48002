import { useState, useEffect } from 'react';
import { Box } from '@mui/material';
// 데이터 목록 컴포넌트
import DataList from './DataList';
import Spinner from 'react-bootstrap/Spinner';
import Pagination from './Pagination';
import { useRejectedMeatListFetch } from '../../API/getRejectedMeatListSWR';

const navy = '#0F3659';

// 반려 데이터 목록 컴포넌트
const RejectedDataListComp = ({
  startDate, // 조회 시작 날짜
  endDate, // 조회 종료 날짜
  pageOffset, // 조회 페이지 offset
}) => {
  // 고기 데이터 목록
  const [meatList, setMeatList] = useState([]);
  // 데이터 전체 개수
  const [totalData, setTotalData] = useState(0);
  // 현재 페이지 번호
  const [currentPage, setCurrentPage] = useState(1);
  // 한페이지당 보여줄 개수
  const count = 6;
  const totalPages = Math.ceil(totalData / count);

  // API fetch 데이터 전처리
  const processRejectedMeatDatas = (data) => {
    // 전체 데이터 수
    setTotalData(data['DB Total len']);
    // 반려데이터
    setMeatList(data['반려']);
  };

  //API fetch
  const { data, isLoading, isError } = useRejectedMeatListFetch(
    currentPage - 1,
    count,
    startDate,
    endDate
  );
  console.log('반려 육류 데이터 fetch 결과:', data, isLoading, isError);

  // 데이터 전처리
  useEffect(() => {
    if (data !== null && data !== undefined) {
      processRejectedMeatDatas(data);
    }
  }, [data]);

  if (data === null) return null;
  // 데이터가 로드되지 않은 경우 로딩중 반환
  if (isLoading)
    return (
      <div>
        <div style={style.listContainer}>
          <Spinner animation="border" />
        </div>
        <Box sx={style.paginationBar}>
          <Pagination
            totalDatas={totalData}
            count={count}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
          />
        </Box>
      </div>
    );
  // 에러인 경우 경고 컴포넌트
  if (isError) return null;

  // 정상 데이터 로드 된 경우
  return (
    <div>
      <div style={style.listContainer}>
        {meatList !== undefined && (
          <DataList
            meatList={meatList}
            pageProp={'reject'}
            offset={currentPage - 1}
            count={count}
            totalPages={totalPages}
            startDate={startDate}
            endDate={endDate}
            pageOffset={pageOffset}
          />
        )}
      </div>
      <Box sx={style.paginationBar}>
        <Pagination
          totalDatas={totalData}
          count={count}
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
        />
      </Box>
    </div>
  );
};

export default RejectedDataListComp;
const style = {
  listContainer: {
    textAlign: 'center',
    width: '100%',
    paddingRight: '0px',
    paddingBottom: '0',
    height: '400px',
  },
  paginationBar: {
    marginTop: '40px',
    width: '100%',
    justifyContent: 'center',
  },
  deletBtnContainer: {
    display: 'flex',
    margin: '20px 0',
    padding: '0px 100px',
    width: '100%',
    justifyContent: 'start',
  },
  deleteBtn: {
    backgroundColor: 'transparent',
    color: navy,
    fontWeight: '600',
  },
};
