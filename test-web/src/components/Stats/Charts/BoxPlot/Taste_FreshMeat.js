import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import CircularProgress from '@mui/material/CircularProgress';
import { apiIP } from '../../../../config';

export default function Taste_FreshMeat({
  startDate,
  endDate,
  animalType,
  grade,
}) {
  const [chartData, setChartData] = useState([]); // Change initial state to null

  const fetchData = async () => {
    try {
      const response = await fetch(
        `http://${apiIP}/meat/statistic/probexpt-stats/fresh?start=${startDate}&end=${endDate}&animalType=${animalType}&grade=${grade}`
      );

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setChartData(data);
    } catch (error) {
      console.error('Error fetching chartData:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, [startDate, endDate, animalType, grade]);

  const calculateBoxPlotStatistics = (data) => {
    const sortedData = data.sort((a, b) => a - b);
    const q1Index = Math.floor(sortedData.length / 4);
    const medianIndex = Math.floor(sortedData.length / 2);
    const q3Index = Math.floor((3 * sortedData.length) / 4);

    const q1 = sortedData[q1Index];
    const median = sortedData[medianIndex];
    const q3 = sortedData[q3Index];
    const min = sortedData[0];
    const max = sortedData[sortedData.length - 1];
    return [min, q1, median, q3, max];
  };

  const chartOptions = {
    chart: {
      type: 'boxPlot',
      height: 350,
    },
  };

  // Conditionally render the chart or CircularProgress based on chartData
  return (
    <div>
      {chartData &&
      chartData.bitterness &&
      chartData.bitterness.unique_values ? (
        <ApexCharts
          series={[
            {
              type: 'boxPlot',
              data: [
                {
                  x: 'bitterness',
                  y: calculateBoxPlotStatistics(
                    chartData.bitterness.unique_values
                  ),
                },
                {
                  x: 'richness',
                  y: calculateBoxPlotStatistics(
                    chartData.richness.unique_values
                  ),
                },
                {
                  x: 'sourness',
                  y: calculateBoxPlotStatistics(
                    chartData.sourness.unique_values
                  ),
                },
                {
                  x: 'umami',
                  y: calculateBoxPlotStatistics(chartData.umami.unique_values),
                },
              ],
            },
          ]}
          options={chartOptions}
          type="boxPlot"
          height={350}
        />
      ) : (
        <CircularProgress />
      )}
    </div>
  );
}
