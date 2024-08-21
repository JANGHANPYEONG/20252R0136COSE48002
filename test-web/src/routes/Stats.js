import { useState, useEffect, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
// mui
import { Box, Container, CircularProgress, Typography } from '@mui/material';
// timezone
import { TIME_ZONE } from '../config';
// 검색 필터 컴포넌트
import SearchFilterBar from '../components/Search/SearchFilterBar';
// 통계 차트 컴포넌트
import StatsTabs from '../components/Stats/StatsTabs';
// 구간 계산 함수
import updateDates from '../Utils/updateDates';

const Stats = () => {
  const s = new Date();
  s.setDate(s.getDate() - 7);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  // 쿼리스트링 추출
  const location = useLocation();
  const { queryStartDate, queryEndDate, queryDuration } = useMemo(() => {
    const searchParams = new URLSearchParams(location.search);
    return {
      queryStartDate: searchParams.get('start') || '',
      queryEndDate: searchParams.get('end') || '',
      queryDuration: searchParams.get('duration') || '',
    };
  }, [location.search]);

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
    <Container maxWidth="xl" style={{ height: '80%' }}>
      <Box
        sx={{
          width: '100%',
          paddingLeft: '210px',
          paddingBottom: '20px',
        }}
      >
        <Typography
          component="h2"
          variant="h4"
          gutterBottom
          style={{
            color: '#151D48',
            fontFamily: 'Poppins',
            fontSize: `30px`,
            fontStyle: 'normal',
            fontWeight: 600,
            // lineHeight: `${(36 / 1920) * 100 * 1.4}vw`,
          }}
        >
          Statistics Analysis
        </Typography>
        <SearchFilterBar setStartDate={setStartDate} setEndDate={setEndDate} />
      </Box>
      <Box
        sx={{
          width: '100%',
          display: 'flex',
          justifyContent: 'center',
          paddingBottom: '20px',
        }}
      >
        <StatsTabs startDate={startDate} endDate={endDate} />
      </Box>
    </Container>
  );
};

export default Stats;
