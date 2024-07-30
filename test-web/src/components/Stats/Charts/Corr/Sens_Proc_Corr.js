import React, { useEffect, useState } from 'react';
import ApexCharts from 'react-apexcharts';
import { statisticSensoryProcessed } from '../../../../API/statistic/statisticSensoryProcessed';

export default function Sense_Proc_Corr({
  startDate,
  endDate,
  animalType,
  grade,
}) {
  const [chartData, setChartData] = useState({});
  const [prop, setProp] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await statisticSensoryProcessed(
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
    color: '색',
    marbling: '마블링',
    overall: '기호도',
    surfaceMoisture: '육즙',
    texture: '조직감',
  };

  // Check if prop is an array, otherwise use an empty array
  const propArray = Array.isArray(prop) ? prop : [];

  const ChartSeries = propArray
    .map((property, rowIndex) => {
      const uniqueValues1 = chartData[property]?.values || [];
      const correlation = new Array(prop.length).fill(0);

      for (let colIndex = 0; colIndex < prop.length; colIndex++) {
        if (colIndex === rowIndex) {
          correlation[colIndex] = 100; // 대각선 위치는 1로 설정
        } else {
          const uniqueValues2 = chartData[prop[colIndex]]?.values || [];

          // 상관 관계 계수 계산
          const correlationCoefficient = calculateCorrelation(
            uniqueValues1,
            uniqueValues2
          );

          correlation[colIndex] = correlationCoefficient;
        }
      }

      return {
        name: axis_labels[property] || property,
        data: correlation.reverse(),
      };
    })
    .reverse();

  // 두 배열의 상관 관계 계수 계산
  function calculateCorrelation(arr1, arr2) {
    if (arr1.length !== arr2.length) {
      return 0;
    }

    const n = arr1.length;

    const sum1 = arr1.reduce((acc, value) => acc + value, 0);
    const sum2 = arr2.reduce((acc, value) => acc + value, 0);

    const sum1Squared = arr1.reduce((acc, value) => acc + value * value, 0);
    const sum2Squared = arr2.reduce((acc, value) => acc + value * value, 0);

    const productSum = arr1
      .map((value, index) => value * arr2[index])
      .reduce((acc, value) => acc + value, 0);

    const numerator = n * productSum - sum1 * sum2;
    const denominator = Math.sqrt(
      (n * sum1Squared - sum1 ** 2) * (n * sum2Squared - sum2 ** 2)
    );

    if (denominator === 0) {
      return 0;
    }

    const correlation = (numerator / denominator) * 100;
    return parseFloat(correlation.toFixed(3)); // 소수점 세 번째 자리까지 반올림
  }

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
      text: '처리육 관능데이터 상관관계',
    },
    grid: {
      padding: {
        right: 20,
      },
    },
    plotOptions: {
      heatmap: {
        colorScale: {
          ranges: [
            {
              from: -100,
              to: -99,
              name: '-100% ~',
              color: '#26578B', // 군청색
            },
            {
              from: -99,
              to: -96,
              name: '-99% ~',
              color: '#456F9B', // 덜 진한 군청색
            },
            {
              from: -96,
              to: -93,
              name: '-96% ~',
              color: '#6487AC', // 중간 군청색
            },
            {
              from: -93,
              to: -80,
              name: '-93% ~',
              color: '#839FBC', // 연한 군청색
            },
            {
              from: -80,
              to: -0.00001,
              name: '-80% ~ 0%',
              color: '#A2B7CD', // 아주 연한 군청색
            },
            {
              from: 0,
              to: 80,
              name: '0% ~ 80%',
              color: '#C89191', // 아주 연한 진홍색
            },
            {
              from: 80,
              to: 93,
              name: '~ 93%',
              color: '#B66D6D', // 연한 진홍색
            },
            {
              from: 93,
              to: 96,
              name: '~ 96%',
              color: '#A44848', // 중간 진홍색
            },
            {
              from: 96,
              to: 99,
              name: '~ 99%',
              color: '#922424', // 덜 진한 진홍색
            },
            {
              from: 99,
              to: 100,
              name: '~ 100%',
              color: '#800000', // 진한 진홍색
            },
            {
              from: 99.99999,
              to: 100,
              name: '100%',
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
