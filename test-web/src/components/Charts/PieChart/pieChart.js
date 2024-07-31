import PropTypes from 'prop-types';
import ReactApexChart from 'react-apexcharts';
// @mui
import { useTheme, styled } from '@mui/material/styles';
import { Card, CardHeader, Button, ButtonGroup, Box } from '@mui/material';
// utils
import { fNumber } from './formatNumber';
// components
import useChart from './helper/usePieChart';
import { useEffect, useState } from 'react';

import { useStatisticPieChart } from '../../../API/statistic/statsticPieChartSWR';
import processPieData from './helper/processPieData';

import handleBtnClick from './helper/handleBtnClick';


const PieChart = ({ subheader, chartColors, startDate, endDate, ...other }) => {
  const theme = useTheme();
  // 전체 또는 소 또는 돼지 중 조회할 데이터의 label
  const [label, setLabel] = useState('total_counts');
  // pie chart에 나타낼 chart series 값
  const [chartSeries, setChartSeries] = useState([]);

  //'useChart' hook과 configuration settings을 사용하여 'chartOptions' 을 정의
  const chartOptions = useChart({
    colors: chartColors, // Colors for the chart series.
    labels: CHART_LABLE, // Labels for the chart.
    stroke: {
      width: 0, // 선의 두께를 0으로 설정
      colors: [theme.palette.background.paper],
    }, // Stroke colors for the chart.
    legend: { floating: true, horizontalAlign: 'center', top: -20 }, // Legend configuration.
    dataLabels: { enabled: true, dropShadow: { enabled: true } }, // Data label configuration
    tooltip: {
      fillSeriesColor: true, // Whether to fill the tooltip with series color.
      y: {
        formatter: (seriesName) => fNumber(seriesName), // Formatter for the y-axis tooltip.
        title: {
          formatter: (seriesName) => `${seriesName}`, // Formatter for the tooltip title.
        },
      },
    },
    plotOptions: {
      pie: {
        donut: {
          labels: {
            show: true,
            name: {
              show: true,
              offsetY: -20, // 이름 위치를 위로 조정
            },
          },
        },
      },
    },
  });

  // pie chart 데이터 API fetch
  const { data, isLoading, isError } = useStatisticPieChart(startDate, endDate);

  // fetch한 데이터 parsing 함수 호출
  useEffect(() => {
    if (data !== null && data !== undefined) {
      processPieData(data, setChartSeries);
    }
    setLabel('total_counts');
  }, [data]);

  return (
    <Card {...other}>
      <CardHeader
        title={TITLE}
        titleTypographyProps={{ variant: 'h6' }}
        style={{ paddingBottom: '0px' }}
      ></CardHeader>
      <Box sx={style.cardWrapper}>
        <ButtonGroup variant="outlined" aria-label="outlined button group">
          <Button
            variant={label === 'total_counts' ? 'contained' : 'outlined'}
            value="total_counts"
            onClick={(e) => handleBtnClick(e, setLabel, setChartSeries, data)}
          >
            전체
          </Button>
          <Button
            variant={label === 'cattle_counts' ? 'contained' : 'outlined'}
            value="cattle_counts"
            onClick={(e) => handleBtnClick(e, setLabel, setChartSeries, data)}
          >
            소
          </Button>
          <Button
            variant={label === 'pig_counts' ? 'contained' : 'outlined'}
            value="pig_counts"
            onClick={(e) => handleBtnClick(e, setLabel, setChartSeries, data)}
          >
            돼지
          </Button>
        </ButtonGroup>
      </Box>

      <StyledChartWrapper dir="ltr" style={{ marginTop: '20px' }}>
        {chartSeries[0] === -1 && chartSeries[1] === -1 ? (
          // 데이터 불러오기 실패한 경우
          <div style={style.chartWrapperDiv}>
            <span>데이터를 불러올 수 없습니다</span>
          </div>
        ) : chartSeries[0] === 0 && chartSeries[1] === 0 ? (
          // 데이터가 없는 경우
          <div style={style.chartWrapperDiv}>
            <span>데이터가 존재하지 않습니다</span>
          </div>
        ) : (
          // 데이터가 있는 경우
          <ReactApexChart
            type="donut"
            series={chartSeries}
            options={chartOptions}
            height={280}
          />
        )}
      </StyledChartWrapper>
    </Card>
  );
};

export default PieChart;

const CHART_HEIGHT = 300;
const LEGEND_HEIGHT = 50;
const TITLE = '신선육/숙성육';
const CHART_LABLE = ['신선육', '숙성육'];

const StyledChartWrapper = styled('div')(({ theme }) => ({
  height: CHART_HEIGHT,
  marginTop: theme.spacing(5),
  '& .apexcharts-canvas svg': { height: CHART_HEIGHT },
  '& .apexcharts-canvas svg,.apexcharts-canvas foreignObject': {
    overflow: 'visible',
  },
  '& .apexcharts-legend': {
    height: LEGEND_HEIGHT,
    alignContent: 'center',
    position: 'relative !important',
    borderTop: `solid 1px ${theme.palette.divider}`,
    top: `calc(${CHART_HEIGHT - LEGEND_HEIGHT}px) !important`,
  },
}));

const style = {
  cardWrapper: {
    display: 'flex',
    width: '100%',
    justifyContent: 'end',
    paddingRight: '20px',
  },
  chartWrapperDiv: {
    width: '100%',
    height: '100%',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
};

PieChart.propTypes = {
  subheader: PropTypes.string,
  chartColors: PropTypes.arrayOf(PropTypes.string),
  chartData: PropTypes.array,
};
