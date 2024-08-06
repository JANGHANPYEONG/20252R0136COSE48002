import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import { statisticProbexptFresh } from '../../../../API/statistic/statisticProbexptFresh';
import calculateHeatMapChartSeries from './calculateHeatMapChartSeries';

const Taste_Fresh_Map = ({ startDate, endDate, animalType, grade }) => {
  const [chartData, setChartData] = useState({});
  const [prop, setProp] = useState([]);

  const fetchData = async () => {
    try {
      const response = await statisticProbexptFresh(
        startDate,
        endDate,
        animalType,
        grade
      );

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setProp(Object.keys(data));
      setChartData(data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, [startDate, endDate, animalType, grade]);

  const y_axis = {
    bitterness: '진한맛',
    richness: '후미',
    sourness: '신맛',
    umami: '감칠맛',
  };

  const ChartSeries = calculateHeatMapChartSeries(prop, chartData, y_axis);
  const ChartOption = {
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
    title: {
      text: '원육 맛데이터 범위별 분포(빈도수)',
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
  };

  return (
    <ApexCharts
      options={ChartOption}
      series={ChartSeries}
      type="heatmap"
      height={350}
    />
  );
};

export default Taste_Fresh_Map;
