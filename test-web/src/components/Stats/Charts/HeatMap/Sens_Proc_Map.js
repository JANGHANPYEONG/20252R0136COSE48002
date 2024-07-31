import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import { statisticSensoryProcessed } from '../../../../API/statistic/statisticSensoryProcessed';

export default function Sens_Proc_Map({
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

  const y_axis = {
    color: '색',
    marbling: '마블링',
    overall: '기호도',
    surfaceMoisture: '육즙',
    texture: '조직감',
  };

  let ChartSeries = [];
  if (prop.length > 0) {
    ChartSeries = prop
      .map((property) => {
        const uniqueValues = chartData[property].values;
        const frequencies = new Array(11).fill(0);

        uniqueValues.forEach((value) => {
          if (value > 10) {
            frequencies[10] += 1;
          } else if (value < 1) {
            frequencies[0] += 1;
          } else {
            const index = Math.floor(value);
            frequencies[index] += 1;
          }
        });

        return {
          name: y_axis[property] || property,
          data: frequencies,
        };
      })
      .reverse();
  }

  const ChartOption = {
    chart: {
      height: 450,
      type: 'heatmap',
    },
    dataLabels: {
      enabled: false,
    },
    xaxis: {
      type: 'numeric',
      tickAmount: 11,
      min: 0,
      max: 11,
    },
    title: {
      text: '처리육 관능데이터 범위별 분포(빈도수)',
    },
    grid: {
      padding: {
        right: 20,
      },
    },
    tooltip: {
      enabled: true,
      y: {
        formatter: function (value, { seriesIndex, dataPointIndex }) {
          const count = ChartSeries[seriesIndex].data[dataPointIndex] || 0;
          const total =
            ChartSeries[seriesIndex].data.reduce((a, b) => a + b, 0) || 1;
          const percentage = ((count / total) * 100).toFixed(1);
          return `${count}개 (${percentage}%)`;
        },
      },
      x: {
        show: true,
        formatter: function (value, { seriesIndex }) {
          const total =
            ChartSeries[seriesIndex]?.data?.reduce((a, b) => a + b, 0) || 0;
          return `${value} ~ ${value + 1}점 [전체 ${total}개]`;
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
