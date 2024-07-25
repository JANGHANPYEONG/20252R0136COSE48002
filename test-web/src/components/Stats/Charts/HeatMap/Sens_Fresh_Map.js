import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import { apiIP } from '../../../../config';

export default function Sens_Fresh_Map({
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
          `http://${apiIP}/meat/statistic/sensory-stats/fresh?start=${startDate}&end=${endDate}&animalType=${animalType}&grade=${grade}`
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

  let ChartSeries = [];
  if (prop.length > 0) {
    ChartSeries = prop.map((property) => {
      const uniqueValues = chartData[property].unique_values;
      const frequencies = new Array(10).fill(0);

      uniqueValues.forEach((value) => {
        const index = Math.floor(value);
        frequencies[index] += 1;
      });

      return {
        name: property,
        data: frequencies,
      };
    });
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
      tickAmount: 10, // Number of ticks on the x-axis
      min: 0,
      max: 10, // Adjust the max value as needed
    },
    title: {
      text: '원육 관능데이터 범위별 분포(빈도수)',
    },
    grid: {
      padding: {
        right: 20,
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
