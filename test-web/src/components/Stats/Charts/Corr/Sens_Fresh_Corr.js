import React, { useEffect, useState } from 'react';
import ApexCharts from 'react-apexcharts';
import { statisticSensoryFresh } from '../../../../API/statistic/statisticSensoryFresh';
import calculateChartSeries from './calculateChartSeries';

export default function Sense_Fresh_Corr({
  startDate,
  endDate,
  animalType,
  grade,
}) {
  const [chartData, setChartData] = useState({});
  const [prop, setProp] = useState([]);

  const fetchData = async () => {
    try {
      const response = await statisticSensoryFresh(
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

  const axis_labels = {
    color: '색',
    marbling: '마블링',
    overall: '기호도',
    surfaceMoisture: '육즙',
    texture: '조직감',
  };

  const ChartSeries = calculateChartSeries(prop, chartData, axis_labels);

  const xCategories = prop
    .slice()
    .reverse()
    .map((p) => axis_labels[p] || p);
  const ChartOption = {
    chart: {
      height: 450,
      width: '100%',
      type: 'heatmap',
      // events: {
      //   mounted: function(chart) {
      //     const styleTag = document.createElement('style');
      //     styleTag.innerHTML = `
      //       .custom-tooltip {
      //         background: #fff;
      //         border: 1px solid #ccc;
      //         padding: 5px 10px;
      //         font-size: 12px;
      //       }
      //     `;
      //     document.head.appendChild(styleTag);
      //   }
      // }
    },
    grid: {
      padding: {
        left: 0, // 왼쪽 여백 제거
        right: 20,
      },
    },
    dataLabels: {
      enabled: false,
    },
    xaxis: {
      type: 'category', // x-axis 데이터 타입을 카테고리로 변경
      categories: xCategories, // 4가지 요소로 구성된 배열을 사용
    },
    title: {
      text: '원육 관능데이터 상관관계',
    },
    grid: {
      padding: {
        right: 20,
      },
    },
    // tooltip: {
    //   enabled: true,
    //   y: {
    //     formatter: function (value) {
    //       const decimalValue = value / 100;
    //       return decimalValue.toFixed(3);
    //     },
    //   },
    // },
    // tooltip: {
    //   enabled: true,
    //   custom: function ({ series, seriesIndex, dataPointIndex, w }) {
    //     const xLabel = w.globals.labels[dataPointIndex];
    //     const yLabel = w.config.series[seriesIndex].name;
    //     const value = series[seriesIndex][dataPointIndex];
    //     const decimalValue = (value / 100).toFixed(3);
    //     return `<div class="custom-tooltip">
    //       <span>${yLabel} - ${xLabel}: ${decimalValue}</span>
    //     </div>`;
    //   },
    // },
    tooltip: {
      enabled: true,
      y: {
        title: {
          formatter: function (value, { seriesIndex, dataPointIndex, w }) {
            const xLabel = w.globals.labels[dataPointIndex];
            const yLabel = w.config.series[seriesIndex].name;
            return `${yLabel} - ${xLabel}:`;
          },
        },
        formatter: function (value) {
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
}
