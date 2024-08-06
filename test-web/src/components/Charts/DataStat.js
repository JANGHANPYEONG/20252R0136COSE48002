//대쉬보드 현황 페이지 통계자료 표출
import PieChart from './PieChart/pieChart';
import StackedBarChart from './StackedBarChart/StackedBarChart';
import Map from './ChoroplethMap/Map';
import { Box } from '@mui/material';
const DataStat = ({ startDate, endDate }) => {
  return (
    <div>
      <Box
        sx={{
          display: 'flex',
          width: '100%',
          height: '100%',
          marginBottom: '10px',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <div style={{ width: '400px', margin: '0px 20px' }}>
          <PieChart
            chartColors={['#3700B3', '#FF0266']}
            startDate={startDate}
            endDate={endDate}
          />
        </div>
        <div style={{ width: '350px', margin: '0px 20px' }}>
          <StackedBarChart startDate={startDate} endDate={endDate} />
        </div>
        <div style={{ margin: '0px 20px' }}>
          <Map startDate={startDate} endDate={endDate} />
        </div>
      </Box>
    </div>
  );
};

export default DataStat;
