const getHeatMapChartOption = (ChartSeries, y_axis) => ({
  chart: {
    height: 450,
    type: 'heatmap',
  },
  dataLabels: {
    enabled: false,
  },
  xaxis: {
    type: 'category',
    categories: [
      '1 미만',
      '1 ~ 2',
      '2 ~ 3',
      '3 ~ 4',
      '4 ~ 5',
      '5 ~ 6',
      '6 ~ 7',
      '7 ~ 8',
      '8 ~ 9',
      '9 ~ 10',
      '10 이상',
    ],
    tickPlacement: 'between',
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
        formatter: (value, { seriesIndex }) => {
          const axisName = ChartSeries[seriesIndex].name;
          const originalProperty = Object.keys(y_axis).find(
            (key) => y_axis[key] === axisName
          );
          return `${axisName}(${originalProperty}):`;
        },
      },
      formatter: (value, { seriesIndex, dataPointIndex }) => {
        const count = ChartSeries[seriesIndex].data[dataPointIndex] || 0;
        const total =
          ChartSeries[seriesIndex].data.reduce((a, b) => a + b, 0) || 1;
        const percentage = ((count / total) * 100).toFixed(1);
        return `${count}개 (${percentage}%)`;
      },
    },
    x: {
      show: true,
      formatter: (value, { dataPointIndex, seriesIndex }) => {
        const categories = [
          '1 미만',
          '1.0 ~ 2.0',
          '2.0 ~ 3.0',
          '3.0 ~ 4.0',
          '4.0 ~ 5.0',
          '5.0 ~ 6.0',
          '6.0 ~ 7.0',
          '7.0 ~ 8.0',
          '8.0 ~ 9.0',
          '9.0 ~ 10.0',
          '10 이상',
        ];
        const total =
          ChartSeries[seriesIndex]?.data?.reduce((a, b) => a + b, 0) || 0;
        return `${categories[dataPointIndex]} [전체 ${total}개]`;
      },
    },
  },
});

export default getHeatMapChartOption;
