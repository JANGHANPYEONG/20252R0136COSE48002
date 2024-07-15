import { useState, useEffect } from 'react';
import { Box, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import Spinner from 'react-bootstrap/Spinner';
import DataList from './DataList';
import Pagination from './Pagination';
import { useMeatListFetch } from '../../API/getMeatListSWR';

// 데이터 목록 조회 페이지 컴포넌트
const DataListComp = ({
  startDate, // 조회 시작 날짜
  endDate, // 조회 종료 날짜
  pageOffset, // 현재 페이지 offset
}) => {
  // 고기 데이터 목록
  const [meatList, setMeatList] = useState([]);
  // 데이터 전체 개수
  const [totalData, setTotalData] = useState(0);
  // 현재 페이지 번호
  const [currentPage, setCurrentPage] = useState(1);
  // 한 페이지당 보여줄 개수
  const [count, setCount] = useState(5);

  // API fetch 데이터 전처리
  const processMeatDatas = (data) => {
    if (!data || !data['DB Total len'] || !data.id_list || !data.meat_dict) {
      console.error('올바르지 않은 데이터 형식:', data);
      return;
    }

    setTotalData(data['DB Total len']);

    let meatData = [];
    data.id_list.forEach((m) => {
      if (data.meat_dict[m]) {
        meatData = [...meatData, data.meat_dict[m]];
      } else {
        console.error('meat_dict에 없는 id:', m);
      }
    });

    setMeatList(meatData);
    console.log(meatData);
  };

  // API fetch
  const { data, isLoading, isError } = useMeatListFetch(
    currentPage - 1,
    count,
    startDate,
    endDate
  );

  // fetch한 데이터 전처리
  useEffect(() => {
    if (data !== null && data !== undefined) {
      processMeatDatas(data);
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
          <div style={style.paginationContainer}>
            <Pagination
              totalDatas={totalData}
              count={count}
              currentPage={currentPage}
              setCurrentPage={setCurrentPage}
            />
            <FormControl variant="outlined" size="small" sx={style.formControl}>
              <InputLabel>Items per page</InputLabel>
              <Select
                value={count}
                onChange={(e) => setCount(e.target.value)}
                label="Items "
              >
                <MenuItem value={5}>5</MenuItem>
                <MenuItem value={10}>10</MenuItem>
                <MenuItem value={20}>20</MenuItem>
              </Select>
            </FormControl>
          </div>
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
            pageProp={'list'} // 육류 목록 페이지임을 명시
            offset={currentPage - 1}
            count={count}
            startDate={startDate}
            endDate={endDate}
            pageOffset={pageOffset}
          />
        )}
      </div>
      <Box sx={style.paginationBar}>
        <div style={style.paginationContainer}>
          <Pagination
            totalDatas={totalData}
            count={count}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
          />
          <FormControl variant="outlined" size="small" sx={style.formControl}>
            <InputLabel>Items per page</InputLabel>
            <Select
              value={count}
              onChange={(e) => setCount(e.target.value)}
              label="Items per page"
            >
              <MenuItem value={5}>5</MenuItem>
              <MenuItem value={10}>10</MenuItem>
              <MenuItem value={20}>20</MenuItem>
            </Select>
          </FormControl>
        </div>
      </Box>
    </div>
  );
};

export default DataListComp;

const style = {
  listContainer: {
    textAlign: 'center',
    width: '100%',
    paddingRight: '0px',
    paddingBottom: '0',
    height: 'auto',
  },
  paginationBar: {
    marginTop: '40px',
    width: '100%',
    justifyContent: 'center',
  },
  paginationContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    minWidth: '640px',
  },
  formControl: {
    minWidth: 120,
    marginLeft: '20px',
  },
};
