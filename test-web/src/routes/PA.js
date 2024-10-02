import { useState, useEffect, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
// mui
import { Box, Button, Select, MenuItem, CircularProgress } from '@mui/material';
// style
import style from './style/pastyle';
// timezone
import { TIME_ZONE } from '../config';
// 검색 필터 컴포넌트
import SearchFilterBar from '../components/Search/SearchFilterBar';
// 예측 육류 목록 컴포넌트
import PADataListComp from '../components/DataListView/PADataListComp';
// ID 검색 컴포넌트
import SearchById from '../components/DataListView/SearchById';
import PASingle from '../components/DataListView/PASingle';
// 구간 계산 함수
import updateDates from '../Utils/updateDates';

const navy = '#0F3659';

// 예측 목록 페이지
const PA = () => {
  const [value, setValue] = useState('list');
  const [specieValue, setSpecieValue] = useState('전체');
  const [singleData, setSingleData] = useState(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [pageOffset, setPageOffset] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  // 쿼리스트링 추출
  const location = useLocation();
  const { querypageOffset, queryStartDate, queryEndDate, queryDuration } =
    useMemo(() => {
      const searchParams = new URLSearchParams(location.search);
      return {
        querypageOffset: searchParams.get('pageOffset'),
        queryStartDate: searchParams.get('start') || '',
        queryEndDate: searchParams.get('end') || '',
        queryDuration: searchParams.get('duration') || '',
      };
    }, [location.search]);

  useEffect(() => {
    setPageOffset(querypageOffset);
  }, [querypageOffset]);

  useEffect(() => {
    setIsLoading(true);
    const now = new Date();
    let start = new Date('1970-01-01T00:00:00Z');
    let end = new Date(now);

    if (queryDuration) {
      const { start: durationStart, end: durationEnd } =
        updateDates(queryDuration);
      start = new Date(durationStart);
      end = new Date(durationEnd);
    } else if (queryStartDate || queryEndDate) {
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
    setIsLoading(false);
  }, [queryStartDate, queryEndDate, queryDuration, location.search]);

  const handleValueChange = (newValue) => {
    setValue(newValue);
  };

  const handleSpeciesChange = (event) => {
    setSpecieValue(event.target.value);
  };

  const handleSingleDataFetch = (fetchedData) => {
    setSingleData(fetchedData);
  };

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

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
            startDate={startDate}
            endDate={endDate}
            specieValue={specieValue}
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
