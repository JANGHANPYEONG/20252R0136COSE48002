import StatsTabs from '../components/Stats/StatsTabs';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import SearchFilterBar from '../components/Search/SearchFilterBar';
import { useState, useEffect, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { TIME_ZONE } from '../config';
import { Typography } from '@mui/material';

const Stats = () => {
  const location = useLocation();
  const { queryStartDate, queryEndDate } = useMemo(() => {
    const searchParams = new URLSearchParams(location.search);
    return {
      queryStartDate: searchParams.get('start') || '',
      queryEndDate: searchParams.get('end') || '',
    };
  }, [location.search]);

  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

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
