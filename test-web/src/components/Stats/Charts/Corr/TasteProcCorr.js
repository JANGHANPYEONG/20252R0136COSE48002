import React, { useEffect, useState } from 'react';
import ApexCharts from 'react-apexcharts';
import { statisticProbexptProcessed } from '../../../../API/statistic/statisticProbexptProcessed';
import calculateChartSeries from './calculateChartSeries';
const TasteProcCorr = ({ startDate, endDate, animalType, grade }) => {
  const [chartData, setChartData] = useState({});
  const [prop, setProp] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await statisticProbexptProcessed(
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

    fetchData();
  }, [startDate, endDate, animalType, grade]);

  const axis_labels = {
    bitterness: '진한맛',
    richness: '후미',
    sourness: '신맛',
    umami: '감칠맛',
  };

  const ChartSeries = calculateChartSeries(prop, chartData, axis_labels);

  const xCategories = prop
    .slice()
    .reverse()
    .map((p) => axis_labels[p] || p);
  const ChartOption = {
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
    title: {
      text: '처리육 맛데이터 상관관계',
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

export default TasteProcCorr;
