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
function PA() {
  const handleDataFetch = (fetchedData) => {
    setData(fetchedData);
  };

  const handleValueChange = (newValue) => {
    setValue(newValue);
  };
  const [value, setValue] = useState('list');
  const [data, setData] = useState(null);
  /**default 조회 날짜 : 현재 날짜 기준 일주일 전  */
  const s = new Date();
  s.setDate(s.getDate() - 7);
  const [startDate, setStartDate] = useState(
    new Date(s.getTime() + TIME_ZONE).toISOString().slice(0, -5)
  );
  const [endDate, setEndDate] = useState(
    new Date(new Date().getTime() + TIME_ZONE).toISOString().slice(0, -5)
  );

  /**설정한 날짜가 있는 경우 쿼리스트링을 통해서 날짜를 저장한 후 추출하여 설정 */
  // 쿼리스트링 추출
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);

  const pageOffset = new URLSearchParams(searchParams).get('pageOffset');
  const queryStartDate = new URLSearchParams(searchParams).get('startDate');
  const queryEndDate = new URLSearchParams(searchParams).get('endDate');
  const queryDuration = searchParams.get('duration');

  const now = new Date();
  let start = new Date(now);
  let end = new Date(now);
  const [specieValue, setSpecieValue] = useState('전체');

  const handleSpeciesChange = (event) => {
    setSpecieValue(event.target.value);
  };

  useEffect(() => {
    if (queryDuration) {
      // duration 파라미터에 따라 시작 날짜 설정
      switch (queryDuration) {
        case 'week':
          start.setDate(now.getDate() - 7);
          break;
        case 'month':
          start.setMonth(now.getMonth() - 1);
          break;
        case 'quarter':
          start.setMonth(now.getMonth() - 3);
          break;
        case 'year':
          start.setFullYear(now.getFullYear() - 1);
          break;
        case 'total':
          start = new Date(1970, 0, 1); // 가장 오래된 날짜로 설정
          break;
        default:
          start.setDate(now.getDate() - 7); // 기본값은 1주일
      }
    } else if (queryStartDate && queryEndDate) {
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
  }, [searchParams]);

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
          Data prediction
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
            onDataFetch={handleDataFetch}
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
      {value === 'single' && <PASingle data={data} />}
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
}
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
