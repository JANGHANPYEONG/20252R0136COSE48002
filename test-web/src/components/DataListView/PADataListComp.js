import { useState, useEffect } from 'react';
import { Box, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import DataList from './DataList';
import Pagination from './Pagination';
import Spinner from 'react-bootstrap/Spinner';
import { usePredictedMeatListFetch } from '../../API/getPredictedMeatListSWR';

// 데이터 예측 페이지 목록 컴포넌트
const PADataListComp = ({ startDate, endDate, pageOffset }) => {
  // 고기 데이터 목록
  const [meatList, setMeatList] = useState([]);
  // 데이터 전체 개수
  const [totalData, setTotalData] = useState(0);
  // 현재 페이지 번호
  const [currentPage, setCurrentPage] = useState(1);
  // 한페이지당 보여줄 개수
  const [count, setCount] = useState(5);

  // API fetch 데이터 전처리
  const processPAMeatDatas = (data) => {
    if (
      !data ||
      !data['DB Total len'] ||
      !Array.isArray(data.id_list) ||
      !data.meat_dict
    ) {
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
  };

  // API fetch
  const { data, isLoading, isError } = usePredictedMeatListFetch(
    currentPage - 1,
    count,
    startDate,
    endDate
  );
  console.log('육류 예측 목록 fetch 결과:', data);

  // fetch한 데이터 전처리
  useEffect(() => {
    if (data !== null && data !== undefined) {
      processPAMeatDatas(data);
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
            pageProp={'pa'}
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

export default PADataListComp;

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
    justifyContent: 'right',
    alignItems: 'center',
    minWidth: '640px',
  },
  formControl: {
    minWidth: 120,
    marginLeft: '20px',
  },
};
