import { useState, useEffect, useMemo } from 'react';
// 검색 필터 컴포넌트
import SearchFilterBar from '../components/Search/SearchFilterBar';
// 목록 컴포넌트
import DataListComp from '../components/DataListView/DataListComp';
// 목록 통계 컴포넌트
import DataStat from '../components/Charts/DataStat';
// 반려 데이터 목록 컴포넌트
import RejectedDataListComp from '../components/DataListView/RejectedDataListComp';
// 엑셀 파일 export/ import 컴포넌트
import ExcelController from '../components/DataListView/ExcelController';
import StatsExport from '../components/DataListView/StatsExport_';
// mui
import { Box, Button, Select, MenuItem } from '@mui/material';
// import timezone
import { TIME_ZONE } from '../config';
// import icon
import { FaBoxOpen } from 'react-icons/fa';
import { useLocation } from 'react-router-dom';
import SearchById from '../components/DataListView/SearchById';
import DataSingle from '../components/DataListView/DataSingle';

const navy = '#0F3659';

const Dashboard = () => {
  const [value, setValue] = useState('list');
  const [specieValue, setSpecieValue] = useState('전체');
  const [singleData, setSingleData] = useState(null);

  // 쿼리스트링 추출
  const location = useLocation();

  const { pageOffset, queryStartDate, queryEndDate } = useMemo(() => {
    const searchParams = new URLSearchParams(location.search);
    return {
      pageOffset: searchParams.get('pageOffset'),
      queryStartDate: searchParams.get('start') || '',
      queryEndDate: searchParams.get('end') || '',
    };
  }, [location.search]);

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
        overflow: 'auto',
        width: '100%',
        marginTop: '100px',
        height: '100%',
        paddingLeft: '30px',
        paddingRight: '20px',
      }}
    >
      {/**페이지 제목 Dashboard ()> 반려함) */}
      <Box
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          minWidth: '634px', // minimum width
        }}
      >
        {value === 'reject' ? (
          <div style={{ display: 'flex' }}>
            <span
              style={{ color: '#b0bec5', fontSize: '30px', fontWeight: '600' }}
            >
              Dashboard {'>'}{' '}
            </span>
            <span
              style={{ color: `${navy}`, fontSize: '30px', fontWeight: '600' }}
            >
              반려함
            </span>
          </div>
        ) : (
          <span
            style={{ color: `${navy}`, fontSize: '30px', fontWeight: '600' }}
          >
            Dashboard
          </span>
        )}

        <div style={{ display: 'flex', justifyContent: 'end' }}>
          <Button
            style={
              value === 'reject'
                ? styles.tabBtnCilcked
                : { color: `${navy}`, border: `1px solid ${navy}` }
            }
            value="reject"
            variant="outlined"
            onClick={(e) => {
              setValue(e.target.value);
            }}
          >
            <FaBoxOpen style={{ marginRight: '3px' }} />
            반려함
          </Button>
        </div>
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
          {value !== 'single' && (
            <Button
              style={value === 'stat' ? styles.tabBtnCilcked : styles.tabBtn}
              value="stat"
              variant="outlined"
              onClick={(e) => {
                setValue(e.target.value);
              }}
            >
              현황
            </Button>
          )}
        </div>
      </Box>

      {/**검색필터, 엑셀  */}
      <Box sx={styles.fixed}>
        <Box
          sx={{ display: 'flex', alignItems: 'center', gap: 2, flexGrow: 1 }}
        >
          <SearchFilterBar />
          {value === 'list' && (
            <>
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
            </>
          )}
        </Box>
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            paddingRight: '85px',
          }}
        >
          {(value === 'list' || value === 'single') && (
            <ExcelController
              startDate={startDate}
              endDate={endDate}
              specieValue={specieValue}
            />
          )}
          {value === 'stat' && <StatsExport />}
        </div>
      </Box>

      {value === 'single' && (
        <DataSingle
          startDate={startDate}
          endDate={endDate}
          singleData={singleData}
        />
      )}

      {value === 'list' && (
        <DataListComp
          startDate={startDate}
          endDate={endDate}
          pageOffset={pageOffset}
          specieValue={specieValue}
        />
      )}
      {value === 'stat' && (
        <DataStat
          startDate={startDate}
          endDate={endDate}
          pageOffset={pageOffset}
        />
      )}
      {value === 'reject' && (
        <RejectedDataListComp
          startDate={startDate}
          endDate={endDate}
          pageOffset={pageOffset}
          specieValue={specieValue}
        />
      )}
    </div>
  );
};

export default Dashboard;

const styles = {
  fixed: {
    zIndex: 1,
    borderRadius: '0',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center', // Add this line to vertically align items
    backgroundColor: 'white',
    margin: '10px 0px',
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
  titleFont: {},
};
