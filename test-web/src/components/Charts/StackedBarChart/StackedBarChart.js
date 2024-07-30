import { useEffect, useState } from 'react';
// material-ui
import { useTheme } from '@mui/material/styles';
// third-party
import ReactApexChart from 'react-apexcharts';
import { useStatisticStackedBar } from '../../../API/statistic/statsticStackedBarSWR';
import processStackedBarData from './helper/processStackedBarData';

const StackedBarChart = ({ startDate, endDate }) => {
  const theme = useTheme();
  const line = theme.palette.divider;
  // 누적 바 차트 부위 별 색
  const stackColors = [
    // 빨강, 주황, 노랑, 초록, 파랑
    theme.palette.error.main,
    theme.palette.warning.main,
    theme.palette.warning.light,
    theme.palette.success.light,
    theme.palette.primary.main,

    '#0322AB', // 짙은 남색
    '#6A1B9A', // 짙은 보라색
    '#C2185B', // 짙은 분홍색
    '#FF4081', // 진홍색

    '#DBC0AF', // 옅은 남색
    '#CE93D8', // 옅은 보라색
    '#F48FB1', // 옅은 분홍색
  ];

  // API fetch 데이터 저장
  const [series, setSeries] = useState([]);

  // 누적 바 데이터 API fetch
  const { data, isLoading, isError } = useStatisticStackedBar(
    startDate,
    endDate
  );
  console.log('stacked bar chart fetch 결과:', data);

  // fetch한 데이터 parsing 함수 호출
  useEffect(() => {
    if (data !== null && data !== undefined) {
      processStackedBarData(data, setSeries);
    }
  }, [data]);

  // stacked bar 스타일
  const [options, setOptions] = useState(columnChartOptions);
  useEffect(() => {
    setOptions((prevState) => ({
      ...prevState,
      colors: stackColors,
      xaxis: {
        categories: ['소', '돼지'],
        labels: {
          style: {
            colors: stackColors,
          },
        },
      },
      yaxis: {
        labels: {
          style: {
            colors: stackColors,
          },
        },
      },
      grid: {
        borderColor: line,
      },
      tooltip: {
        theme: 'light',
      },
    }));
  }, []);

  return (
    <div
      id="chart"
      style={{
        backgroundColor: '#f4f6f8',
        borderRadius: '10px',
        padding: '10px',
        boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
      }}
    >
      <ReactApexChart
        type="bar"
        options={options}
        series={series}
        height={450}
      />
    </div>
  );
};

export default StackedBarChart;

// chart options
const columnChartOptions = {
  chart: {
    type: 'bar',
    height: 350,
    stacked: true,
    toolbar: {
      show: true,
    },
    zoom: {
      enabled: true,
    },
  },
  responsive: [
    {
      breakpoint: 480,
      options: {
        legend: {
          position: 'bottom',
          offsetX: -10,
          offsetY: 0,
        },
      },
    },
  ],
  plotOptions: {
    bar: {
      horizontal: false,
      borderRadius: 0,
      dataLabels: {
        total: {
          enabled: true,
          style: {
            fontSize: '13px',
            fontWeight: 900,
          },
        },
      },
    },
  },
  dataLabels: {
    enabled: false,
  },
  stroke: {
    show: true,
    width: 0,
    colors: ['transparent'],
  },
  xaxis: {
    categories: ['소', '돼지'],
  },
  yaxis: {
    title: {
      text: '개',
    },
  },
  fill: {
    opacity: 1,
  },
  tooltip: {
    y: {
      formatter(val) {
        return `${val}개`;
      },
    },
  },
  legend: {
    show: true,
    fontFamily: `'Public Sans', sans-serif`,
    offsetX: 10,
    offsetY: 10,
    labels: {
      useSeriesColors: false,
    },
    markers: {
      width: 16,
      height: 16,
      radius: '50%',
      offsexX: 2,
      offsexY: 2,
    },
    itemMargin: {
      horizontal: 10,
      vertical: 20,
    },
  },
};
