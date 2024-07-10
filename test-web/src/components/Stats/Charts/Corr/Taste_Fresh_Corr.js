import React, { useEffect, useState } from 'react';
import ApexCharts from 'react-apexcharts';
import { apiIP } from '../../../../config';

export default function Taste_Fresh_Corr({
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
        const response = await fetch(
          `http://${apiIP}/meat/statistic/probexpt-stats/fresh?start=${startDate}&end=${endDate}&animalType=${animalType}&grade=${grade}`
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

  // Check if prop is an array, otherwise use an empty array
  const propArray = Array.isArray(prop) ? prop : [];

  const ChartSeries = propArray.map((property, rowIndex) => {
    const uniqueValues1 = chartData[property]?.unique_values || [];
    const correlation = new Array(prop.length).fill(0);

    for (let colIndex = 0; colIndex < prop.length; colIndex++) {
      if (colIndex === rowIndex) {
        correlation[colIndex] = 1; // 대각선 위치는 1로 설정
      } else {
        const uniqueValues2 = chartData[prop[colIndex]]?.unique_values || [];

        // 상관 관계 계수 계산
        const correlationCoefficient = calculateCorrelation(
          uniqueValues1,
          uniqueValues2
        );

        correlation[colIndex] = correlationCoefficient;
      }
    }

    return {
      name: property,
      data: correlation,
    };
  });

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

    return numerator / denominator;
  }

  const xCategories = prop;
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
      text: '원육 맛데이터 상관관계',
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
              from: 0,
              to: 0.8,
              name: ' 0 - 80 % ',
              color: '#CCCCCC', // 연한회색
            },
            {
              from: 0.8,
              to: 0.93,
              name: ' 80 - 93 % ',
              color: '#999999', // 덜연한회색
            },
            {
              from: 0.93,
              to: 0.96,
              name: ' 93 - 96 % ',
              color: '#777777', // 회색
            },
            {
              from: 0.96,
              to: 0.99,
              name: ' 96 - 99 % ',
              color: '#444444', // 될진한회색
            },
            {
              from: 0.99,
              to: 1.0,
              name: ' 99 - 100 % ',
              color: '#111111', // 진한회색
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
