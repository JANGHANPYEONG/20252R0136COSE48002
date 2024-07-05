import StatsTabs from '../components/Stats/StatsTabs';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import SearchFilterBar from '../components/Search/SearchFilterBar';
import { useState } from 'react';
import { TIME_ZONE } from '../config';
import { Typography } from '@mui/material';

function Stats() {
  const s = new Date();
  s.setDate(s.getDate() - 7);
  const [startDate, setStartDate] = useState(
    new Date(s.getTime() + TIME_ZONE).toISOString().slice(0, -5)
  );
  const [endDate, setEndDate] = useState(
    new Date(new Date().getTime() + TIME_ZONE).toISOString().slice(0, -5)
  );

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
            fontSize: `${(36 / 1920) * 100}vw`,
            fontStyle: 'normal',
            fontWeight: 600,
            lineHeight: `${(36 / 1920) * 100 * 1.4}vw`,
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
