import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import { apiIP } from '../../../../config';

export default function Taste_Fresh_Map({ startDate, endDate }) {
  const [chartData, setChartData] = useState({});
  const [prop, setProp] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          `http://${apiIP}/meat/statistic/probexpt-stats/fresh?start=${startDate}&end=${endDate}`
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
  }, [startDate, endDate]);

  // Check if prop is an array, otherwise use an empty array
  const propArray = Array.isArray(prop) ? prop : [];

  const ChartSeries = propArray.map((property) => {
    const uniqueValues = chartData[property]?.unique_values || [];
    const frequencies = new Array(10).fill(0);

    uniqueValues.forEach((value) => {
      const index = Math.floor(value);
      if (index >= 0 && index < frequencies.length) {
        frequencies[index] += 1;
      }
    });

    return {
      name: property,
      data: frequencies,
    };
  });

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
      text: '원육 맛데이터 범위별 분포(빈도수)',
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
