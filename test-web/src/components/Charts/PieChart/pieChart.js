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
  const { data, isLoading, isError } = usePieChartFetch(startDate, endDate);
  console.log('pie chart fetch 결과:', data);

  // fetch한 JSON 데이터에서 필요한 값 parsing 및 chartSeries에 저장
  // 렌더링 시 데이터 받지 못하면 -1, -1
  const processPieData = (data) => {
    if (
      data &&
      'total_counts' in data &&
      'raw' in data.total_counts &&
      'processed' in data.total_counts
    ) {
      const raw = data.total_counts.raw;
      const processed = data.total_counts.processed;

      setChartSeries([
        !Number.isNaN(raw) ? raw : -1,
        !Number.isNaN(processed) ? processed : -1,
      ]);
    } else {
      console.log('Invalid data structure:', data);
      setChartSeries([-1, -1]); // Default to [-1, -1] if data is invalid
    }
  };

  // fetch한 데이터 parsing 함수 호출
  useEffect(() => {
    if (data !== null && data !== undefined) {
      processPieData(data);
    }
  }, [data]);

  // 토글 버튼 handle (전체, 소, 돼지)
  const handleBtnClick = (e) => {
    const value = e.target.value;
    let newChartSeries = [-1, -1]; // 기본값으로 [-1, -1]을 설정

    if (data && data !== null && data !== undefined && value in data) {
      const categoryData = data[value];
      if (
        categoryData &&
        'raw' in categoryData &&
        'processed' in categoryData
      ) {
        const raw = categoryData.raw;
        const processed = categoryData.processed;

        newChartSeries = [
          !Number.isNaN(raw) ? raw : -1,
          !Number.isNaN(processed) ? processed : -1,
        ];
      }
    } else {
      console.log('Invalid data structure:', value);
    }

    setLabel(value);
    setChartSeries(newChartSeries);
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
