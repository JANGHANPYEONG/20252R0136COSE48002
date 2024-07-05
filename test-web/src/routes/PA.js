import { useState, useEffect } from 'react';
import SearchFilterBar from '../components/Search/SearchFilterBar';
// 데이터 목록
import PADataListComp from '../components/DataListView/PADataListComp';
// mui
import { Box } from '@mui/material';
// import timezone
import { TIME_ZONE } from '../config';
import { useLocation } from 'react-router-dom';

const navy = '#0F3659';

// 예측 목록 페이지
function PA() {
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
      {/**검색 필터 */}
      <Box sx={styles.fixed}>
        <SearchFilterBar setStartDate={setStartDate} setEndDate={setEndDate} />
      </Box>
      {/**데이터 목록 */}
      <PADataListComp startDate={startDate} endDate={endDate} />
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
};
