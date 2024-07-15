import StatsTabs from '../components/Stats/StatsTabs';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import SearchFilterBar from '../components/Search/SearchFilterBar';
import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { TIME_ZONE } from '../config';
import { Typography } from '@mui/material';

function Stats() {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);

  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    const queryStartDate = searchParams.get('startDate');
    const queryEndDate = searchParams.get('endDate');
    const queryDuration = searchParams.get('duration');

    const now = new Date();
    let start = new Date(now);
    let end = new Date(now);

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
    <Container maxWidth="xl">
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
}

export default Stats;
