const getCorrChartOption = (xCategories) => ({
  chart: {
    height: 450,
    type: 'heatmap',
  },
  dataLabels: {
    enabled: false,
  },
  xaxis: {
    type: 'category', // x-axis 데이터 타입을 카테고리로 변경
    categories: xCategories, // 4가지 요소로 구성된 배열을 사용
  },
  grid: {
    padding: {
      right: 20,
    },
  },
  tooltip: {
    enabled: true,
    y: {
      title: {
        formatter: (value, { seriesIndex, dataPointIndex, w }) => {
          const xLabel = w.globals.labels[dataPointIndex];
          const yLabel = w.config.series[seriesIndex].name;
          return `${yLabel} - ${xLabel}:`;
        },
      },
      formatter: (value) => {
        const decimalValue = (value / 100).toFixed(3);
        return `${decimalValue}`;
      },
    },
  },
  plotOptions: {
    heatmap: {
      colorScale: {
        ranges: [
          {
            from: -100,
            to: -99,
            name: '-1 ~',
            color: '#26578B', // 군청색
          },
          {
            from: -99,
            to: -96,
            name: '-0.99 ~',
            color: '#456F9B', // 덜 진한 군청색
          },
          {
            from: -96,
            to: -93,
            name: '-0.96 ~',
            color: '#6487AC', // 중간 군청색
          },
          {
            from: -93,
            to: -80,
            name: '-0.93 ~',
            color: '#839FBC', // 연한 군청색
          },
          {
            from: -80,
            to: -0.00001,
            name: '-0.80 ~ 0',
            color: '#A2B7CD', // 아주 연한 군청색
          },
          {
            from: 0,
            to: 80,
            name: '0 ~ 0.80',
            color: '#C89191', // 아주 연한 진홍색
          },
          {
            from: 80,
            to: 93,
            name: '~ 0.93',
            color: '#B66D6D', // 연한 진홍색
          },
          {
            from: 93,
            to: 96,
            name: '~ 0.96',
            color: '#A44848', // 중간 진홍색
          },
          {
            from: 96,
            to: 99,
            name: '~ 0.99',
            color: '#922424', // 덜 진한 진홍색
          },
          {
            from: 99,
            to: 99.99999,
            name: '~ 1',
            color: '#800000', // 진한 진홍색
          },
          {
            from: 99.99999,
            to: 100,
            name: '1',
            color: '#000000', // 검정색(자기자신과의 상관계수)
          },
        ],
      },
    },
  },
});

export default getCorrChartOption;
