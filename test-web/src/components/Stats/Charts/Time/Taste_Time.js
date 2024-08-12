import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import { statisticTime } from '../../../../API/statistic/statisticTime';

const Taste_Time = ({ startDate, endDate, seqnoValue, meatValue }) => {
  const fetchData = async () => {
    try {
      const response = await statisticTime(startDate, endDate, seqnoValue, meatValue);
      const freshmeat = await statisticTime(startDate, endDate, 1, meatValue) //시계열 api 호출
      const data = await response.json();
      const freshmeat_data = await freshmeat.json()

      // Extract the necessary data from the response
      const deepAgingData = [
        parseFloat(data[0].toFixed(2)), // 0일
        parseFloat(data[1].toFixed(2)), // 3일
        parseFloat(data[2].toFixed(2)), // 7일
        parseFloat(data[3].toFixed(2)), // 14일
        parseFloat(data[4].toFixed(2)), // 21일
      ];

      const rawMeatData = [
        parseFloat(freshmeat_data[1].toFixed(2)), 
        parseFloat(freshmeat_data[1].toFixed(2)), // 원육 데이터를 각 시점에 맞추어 반복
        parseFloat(freshmeat_data[1].toFixed(2)),
        parseFloat(freshmeat_data[1].toFixed(2)),
        parseFloat(freshmeat_data[1].toFixed(2)),
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

  useEffect(() => {
    fetchData();
  }, [startDate, endDate, meatValue, seqnoValue]);

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
      categories: ['0일','3일', '7일', '14일', '21일'],
      title: {
        text: '숙성일',
      },
    },
    yaxis: {
      title: {
        text: '연도 (Tenderness)',
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
};

export default Taste_Time;
