import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import CircularProgress from '@mui/material/CircularProgress';
import { statisticSensoryHeated } from '../../../../API/statistic/statisticSensoryHeated';
import calculateBoxPlotStatistics from './calculateBoxPlotStat';

const Sens_HeatedMeat = ({ startDate, endDate, animalType, grade }) => {
  const [chartData, setChartData] = useState([]);

  const fetchData = async () => {
    try {
      const response = await statisticSensoryHeated(
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
      text: '가열육 관능데이터 박스 플롯(Box Plot) 분포',
    },
  };

  // Conditionally render the chart only when chartData is not empty
  return (
    <div>
      {chartData && chartData.flavor && chartData.flavor.values ? (
        <ApexCharts
          series={[
            {
              type: 'boxPlot',
              data: [
                {
                  x: '풍미(flavor)',
                  y: calculateBoxPlotStatistics(chartData.flavor.values),
                },
                {
                  x: '다즙성(juiciness)',
                  y: calculateBoxPlotStatistics(chartData.juiciness.values),
                },
                {
                  x: '기호도(palatability)',
                  y: calculateBoxPlotStatistics(chartData.palatability.values),
                },
                {
                  x: '연도(tenderness)',
                  y: calculateBoxPlotStatistics(chartData.tenderness.values),
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
};

export default Sens_HeatedMeat;
