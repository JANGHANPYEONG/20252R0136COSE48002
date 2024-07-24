import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import { apiIP } from '../../../../config';

export default function Taste_Time({ startDate, endDate, meatValue }) {
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          `http://${apiIP}/meat/statistic/sensory-stats/heated-fresh?start=${startDate}&end=${endDate}&meatValue=${meatValue}`
        );

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        const data = await response.json();

        // Calculate the average values for each property (bitterness, richness, sourness, umami)
        const properties = ['bitterness', 'richness', 'sourness', 'umami'];
        const sum = {};
        const counts = {};
        for (const time in data) {
          for (const prop of properties) {
            sum[time] ??= {};
            counts[time] ??= {};
            for (const key in data[time]) {
              sum[time][prop] = (sum[time][prop] || 0) + data[time][key][prop];
              counts[time][prop] = (counts[time][prop] || 0) + 1;
            }
          }
        }
        const averages = {};

        for (const time in data) {
          averages[time] ??= {};
          for (const prop of properties) {
            if (sum[time][prop]) {
              averages[time][prop] = sum[time][prop] / counts[time][prop];
            } else {
              averages[time][prop] = 0;
            }
          }
        }

        setAverages(averages);
        // Update the chart data
        setSeries([
          {
            name: 'Bitterness',
            data: Object.keys(averages).map((time) =>
              parseFloat(averages[time].bitterness)
            ),
          },
          {
            name: 'Richness',
            data: Object.keys(averages).map((time) =>
              parseFloat(averages[time].richness)
            ),
          },
          {
            name: 'Sourness',
            data: Object.keys(averages).map((time) =>
              parseFloat(averages[time].sourness)
            ),
          },
          {
            name: 'Umami',
            data: Object.keys(averages).map((time) =>
              parseFloat(averages[time].umami)
            ),
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
      name: 'Bitterness',
      data: [], // We will update this with the actual data points later
    },
    {
      name: 'Richness',
      data: [], // We will update this with the actual data points later
    },
    {
      name: 'Sourness',
      data: [], // We will update this with the actual data points later
    },
    {
      name: 'Umami',
      data: [], // We will update this with the actual data points later
    },
  ]);

  const [averages, setAverages] = useState({});
  console.log('key', averages);

  // Initialize propertyMin and propertyMax with the first data point values
  const firstTime = Object.keys(averages)[0];
  const propertyMin = { ...averages[firstTime] };
  const propertyMax = { ...averages[firstTime] };

  for (const time in averages) {
    for (const prop in averages[time]) {
      const value = averages[time][prop];
      if (value < propertyMin[prop]) {
        propertyMin[prop] = value;
      }
      if (value > propertyMax[prop]) {
        propertyMax[prop] = value;
      }
    }
  }

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
    colors: ['#77B6EA', '#545454', '#F44336', '#4CAF50'],
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
      categories: Object.keys(averages).map((time) => time),
      title: {
        text: '숙성 시간',
      },
    },
    yaxis: {
      title: {
        text: '맛 데이터',
      },
      min:
        Math.min(
          propertyMin.bitterness,
          propertyMin.richness,
          propertyMin.sourness,
          propertyMin.umami
        ) - 5,
      max:
        Math.max(
          propertyMax.bitterness,
          propertyMax.richness,
          propertyMax.sourness,
          propertyMax.umami
        ) + 5,
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
