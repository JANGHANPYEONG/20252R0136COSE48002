import { useState, useEffect } from 'react';
import SearchFilterBar from '../components/Search/SearchFilterBar';
// 데이터 목록
import PADataListComp from '../components/DataListView/PADataListComp';
// mui
import { Box, Button } from '@mui/material';
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
  const [value, setValue] = useState('list')
  const [data, setData] = useState(null)
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
  const searchParams = useLocation().search;
  //const pageOffset = new URLSearchParams(searchParams).get('pageOffset');
  const queryStartDate = new URLSearchParams(searchParams).get('startDate');
  const queryEndDate = new URLSearchParams(searchParams).get('endDate');
  const pageOffset = new URLSearchParams(searchParams).get('pageOffset');

  useEffect(() => {
    if (queryStartDate && queryEndDate) {
      setStartDate(queryStartDate);
      setEndDate(queryEndDate);
    }
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
        <span style={{ color: `${navy}`, fontSize: '30px', fontWeight: '600' }}>
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
        </Box>
      </Box>
      {/**데이터 목록 */}
      {value === 'single' && <PASingle data={data} />}
      {value === 'list' && (
        <PADataListComp
          startDate={startDate}
          endDate={endDate}
          pageOffset={pageOffset}
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
