import { useState, useEffect, useMemo } from 'react';
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
import style from './style/pastyle';
import updateDates from '../Utils/updateDates';

const navy = '#0F3659';

// 예측 목록 페이지
const PA = () => {
  const [value, setValue] = useState('list');
  const [singleData, setSingleData] = useState(null);
  const [specieValue, setSpecieValue] = useState('전체');

  // 쿼리스트링 추출
  const location = useLocation();
  const { querypageOffset, queryStartDate, queryEndDate } = useMemo(() => {
    const searchParams = new URLSearchParams(location.search);
    return {
      querypageOffset: searchParams.get('pageOffset'),
      queryStartDate: searchParams.get('start') || '',
      queryEndDate: searchParams.get('end') || '',
    };
  }, [location.search]);

  const s = new Date();
  s.setDate(s.getDate() - 7);
  const [startDate, setStartDate] = useState(s.toISOString().slice(0, -5));
  const [endDate, setEndDate] = useState(new Date().toISOString().slice(0, -5));
  const [pageOffset, setPageOffset] = useState(1);

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
    setPageOffset(querypageOffset);
  }, [querypageOffset]);

  useEffect(() => {
    const now = new Date();
    let start = new Date('1970-01-01T00:00:00Z');
    let end = new Date(now);

    if (queryStartDate || queryEndDate) {
      // startDate 또는 endDate 파라미터가 있을 경우
      if (queryStartDate) {
        start = new Date(queryStartDate);
      }
      if (queryEndDate) {
        end = new Date(queryEndDate);
      }
    } else {
      // 기본값 설정 (7일 전부터 현재까지)
      start = new Date(now);
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
  }, [queryStartDate, queryEndDate, location.search]);

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
      <Box sx={style.fixedTab}>
        <div style={{ display: 'flex' }}>
          <Button
            style={value === 'list' ? style.tabBtnCilcked : style.tabBtn}
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
      <Box sx={style.fixed}>
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
