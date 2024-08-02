import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import CircularProgress from '@mui/material/CircularProgress';
import { statisticProbexptProcessed } from '../../../../API/statistic/statisticProbexptProcessed';
import calculateBoxPlotStatistics from './calculateBoxPlotStat';

export default function Taste_ProcMeat({
  startDate,
  endDate,
  animalType,
  grade,
}) {
  const [chartData, setChartData] = useState([]);

  const fetchData = async () => {
    try {
      const response = await statisticProbexptProcessed(
        startDate,
        endDate,
        animalType,
        grade
      );

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setChartData(data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  useEffect(() => {
    fetchData();
  }, [startDate, endDate, animalType, grade]);

  const chartOptions = {
    chart: {
      type: 'boxPlot',
      height: 350,
    },
    title: {
      text: '처리육 맛데이터 박스 플롯(Box Plot) 분포',
    },
  };

  // Conditionally render the chart only when chartData is not empty
  return (
    <div>
      {chartData && chartData.bitterness && chartData.bitterness.values ? (
        <ApexCharts
          series={[
            {
              type: 'boxPlot',
              data: [
                {
                  x: '진한맛(bitterness)',
                  y: calculateBoxPlotStatistics(chartData.bitterness.values),
                },
                {
                  x: '후미(richness)',
                  y: calculateBoxPlotStatistics(chartData.richness.values),
                },
                {
                  x: '신맛(sourness)',
                  y: calculateBoxPlotStatistics(chartData.sourness.values),
                },
                {
                  x: '감칠맛(umami)',
                  y: calculateBoxPlotStatistics(chartData.umami.values),
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
