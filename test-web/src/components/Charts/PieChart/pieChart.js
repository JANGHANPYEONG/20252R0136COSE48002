import PropTypes from 'prop-types';
import ReactApexChart from 'react-apexcharts';
// @mui
import { useTheme, styled } from '@mui/material/styles';
import { Card, CardHeader, Button, ButtonGroup, Box } from '@mui/material';
// utils
import { fNumber } from './formatNumber';
// components
import useChart from './usePieChart';
import { useEffect, useState } from 'react';

import { usePieChartFetch } from '../../../API/listCharts/getPieChartSWR';

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
    legend: { floating: true, horizontalAlign: 'center' }, // Legend configuration.
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
      pie: { donut: { labels: { show: true } } }, // Plot options for a donut chart. (가운데 설명 표시)
    },
  });

  // fetch한 JSON 데이터에서 필요한 값 parsing 및 chartSeries에 저장
  const processPieData = (data) => {
    setChartSeries([
      data['total_counts']['raw'],
      data['total_counts']['processed'],
    ]);
  };

  // pie chart 데이터 API fetch
  const { data, isLoading, isError } = usePieChartFetch(startDate, endDate);
  console.log('pie chart fetch 결과:', data);

  // fetch한 데이터 parsing 함수 호출
  useEffect(() => {
    if (data !== null && data !== undefined) {
      processPieData(data);
    }
  }, [data]);

  // 토글 버튼 handle (전체, 소, 돼지)
  const handleBtnClick = (e) => {
    const value = e.target.value;
    const chart_series = [data[value]['raw'], data[value]['processed']];
    setLabel(value);
    setChartSeries(chart_series);
  };

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
            onClick={(e) => handleBtnClick(e)}
          >
            전체
          </Button>
          <Button
            variant={label === 'cattle_counts' ? 'contained' : 'outlined'}
            value="cattle_counts"
            onClick={(e) => handleBtnClick(e)}
          >
            소
          </Button>
          <Button
            variant={label === 'pig_counts' ? 'contained' : 'outlined'}
            value="pig_counts"
            onClick={(e) => handleBtnClick(e)}
          >
            돼지
          </Button>
        </ButtonGroup>
      </Box>

      <StyledChartWrapper dir="ltr" style={{ marginTop: '20px' }}>
        {chartSeries[0] === 0 && chartSeries[1] === 0 ? (
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
