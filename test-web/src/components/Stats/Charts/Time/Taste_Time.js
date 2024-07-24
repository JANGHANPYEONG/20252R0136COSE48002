// import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import { apiIP } from '../../../../config';

export default function Taste_Time({ startDate, endDate, meatValue }) {
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          `http://${apiIP}/meat/statistic/time?start=${startDate}&end=${endDate}&meatValue=${meatValue}`
        );

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();

        // Extract the necessary data from the response
        const deepAgingData = [
          data[1], // 3일
          data[2], // 7일
          data[3], // 14일
          data[4], // 21일
        ];
        
        const rawMeatData = [
          data[0], // 원육 데이터를 각 시점에 맞추어 반복
          data[0],
          data[0],
          data[0],
        ];

        // Update the chart data
        setSeries([
          {
            name: 'Deep Aging',
            data: deepAgingData,
          },
          {
            name: 'Raw Meat',
            data: rawMeatData,
          },
        ]);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [startDate, endDate]);

  const [series, setSeries] = useState([
    {
      name: 'Deep Aging',
      data: [], // We will update this with the actual data points later
    },
    {
      name: 'Raw Meat',
      data: [], // We will update this with the actual data points later
    },
  ]);

  const options = {
    chart: {
      height: 350,
      type: 'line',
      dropShadow: {
        enabled: true,
        color: '#000',
        top: 18,
        left: 7,
        blur: 10,
        opacity: 0.2,
      },
      toolbar: {
        show: false,
      },
    },
    colors: ['#77B6EA', '#545454'],
    dataLabels: {
      enabled: true,
    },
    stroke: {
      curve: 'smooth',
    },
    title: {
      text: '숙성 시간에 따른 맛 데이터 변화',
      align: 'left',
    },
    grid: {
      borderColor: '#e7e7e7',
      row: {
        colors: ['#f3f3f3', 'transparent'],
        opacity: 0.5,
      },
    },
    markers: {
      size: 1,
    },
    xaxis: {
      categories: ['3일', '7일', '14일', '21일'],
      title: {
        text: '숙성 시간',
      },
    },
    yaxis: {
      title: {
        text: '맛 데이터 (tenderness)',
      },
      min: 0,
      max: 10,
      labels: {
        formatter: (value) => parseFloat(value).toFixed(2), // Format the y-axis labels to 2 decimal places
      },
    },
    legend: {
      position: 'top',
      horizontalAlign: 'right',
      floating: true,
      offsetY: -25,
      offsetX: -5,
    },
  };

  return (
    <div>
      <div id="chart">
        <ApexCharts
          options={options}
          series={series}
          type="line"
          height={350}
        />
      </div>
    </div>
  );
}
