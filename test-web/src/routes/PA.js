import { useState, useEffect } from 'react';
import SearchFilterBar from '../components/Search/SearchFilterBar';
// 데이터 목록
import PADataListComp from '../components/DataListView/PADataListComp';
// mui
import { Box, Button, Select, MenuItem } from '@mui/material';
// import timezone
import { TIME_ZONE } from '../config';
import { useLocation } from 'react-router-dom';
import SearchById from '../components/DataListView/SearchById';
import PASingle from '../components/DataListView/PASingle';

const navy = '#0F3659';

// 예측 목록 페이지
const PA = () => {
  const [value, setValue] = useState('list');
  const [singleData, setSingleData] = useState(null);
  const [specieValue, setSpecieValue] = useState('전체');

  // 쿼리스트링 추출
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);

  const pageOffset = new URLSearchParams(searchParams).get('pageOffset');

  const queryStartDate = searchParams.get('start') || '';
  const queryEndDate = searchParams.get('end') || '';

  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const handleValueChange = (newValue) => {
    setValue(newValue);
  };

  const handleSpeciesChange = (event) => {
    setSpecieValue(event.target.value);
  };

  const handleSingleDataFetch = (fetchedData) => {
    setSingleData(fetchedData);
  };

  useEffect(() => {
    const now = new Date();
    let start = new Date(now);
    let end = new Date(now);

    if (queryStartDate && queryEndDate) {
      // startDate와 endDate 파라미터가 있을 경우
      start = new Date(queryStartDate);
      end = new Date(queryEndDate);
    } else {
      // 기본값 설정 (7일 전부터 현재까지)
      start.setDate(now.getDate() - 7);
    }

    const formattedStartDate = new Date(start.getTime() + TIME_ZONE)
      .toISOString()
      .slice(0, -5);
    const formattedEndDate = new Date(end.getTime() + TIME_ZONE)
      .toISOString()
      .slice(0, -5);

    setStartDate(formattedStartDate);
    setEndDate(formattedEndDate);
  }, [queryStartDate, queryEndDate]);

  return (
    <div
      style={{
        overflow: 'overlay',
        width: '100%',
        marginTop: '100px',
        height: '100%',
        paddingLeft: '30px',
        paddingRight: '20px',
      }}
    >
      {/**페이지 제목 */}
      <Box
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <span
          style={{
            color: `${navy}`,
            fontSize: '30px',
            fontWeight: '600',
            minWidth: '720px', //720보다 좀 더 작아도 됨
          }}
        >
          Data Prediction
        </span>
      </Box>
      {/**이동 탭 (목록, 통계 , 반려) */}
      <Box sx={styles.fixedTab}>
        <div style={{ display: 'flex' }}>
          <Button
            style={value === 'list' ? styles.tabBtnCilcked : styles.tabBtn}
            value="list"
            variant="outlined"
            onClick={(e) => {
              setValue(e.target.value);
            }}
          >
            목록
          </Button>
        </div>
      </Box>
      {/**검색 필터 */}
      <Box sx={styles.fixed}>
        <Box
          sx={{ display: 'flex', alignItems: 'center', gap: 2, flexGrow: 1 }}
        >
          <SearchFilterBar
            setStartDate={setStartDate}
            setEndDate={setEndDate}
          />
          <SearchById
            onDataFetch={handleSingleDataFetch}
            onValueChange={handleValueChange}
          />
          <Select
            labelId="species"
            id="species"
            value={specieValue}
            onChange={handleSpeciesChange}
            label="종류"
          >
            <MenuItem value="전체">전체</MenuItem>
            <MenuItem value="소">소</MenuItem>
            <MenuItem value="돼지">돼지</MenuItem>
          </Select>
        </Box>
      </Box>
      {/**데이터 목록 */}
      {value === 'single' && <PASingle singleData={singleData} />}
      {value === 'list' && (
        <PADataListComp
          startDate={startDate}
          endDate={endDate}
          pageOffset={pageOffset}
          specieValue={specieValue}
        />
      )}
    </div>
  );
};
export default PA;

const styles = {
  fixed: {
    zIndex: 1,
    borderRadius: '0',
    display: 'flex',
    justifyContent: 'space-between',
    backgroundColor: 'white',
    margin: '10px 0px',
    borderBottom: 'solid rgba(0, 0, 0, 0.12)',
    borderBottomWidth: 'thin',
    minWidth: '720px', // 특정 픽셀 이하로 줄어들지 않도록 설정
  },
  fixedTab: {
    right: '0',
    left: '0px',
    borderRadius: '0',
    display: 'flex',
    justifyContent: 'space-between',
    marginTop: '30px',
    borderBottom: 'solid rgba(0, 0, 0, 0.12)',
    borderBottomWidth: 'thin',
    minWidth: '720px', // 특정 픽셀 이하로 줄어들지 않도록 설정
  },
  tabBtn: {
    border: 'none',
    color: navy,
  },
  tabBtnCilcked: {
    border: `1px solid ${navy}`,
    color: navy,
  },
};
