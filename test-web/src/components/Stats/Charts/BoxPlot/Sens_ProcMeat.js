import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import CircularProgress from '@mui/material/CircularProgress';
import { statisticSensoryProcessed } from '../../../../API/statistic/statisticSensoryProcessed';
import calculateBoxPlotStatistics from './calculateBoxPlotStat';

const Sens_ProcMeat = ({ startDate, endDate, animalType, grade }) => {
  const [chartData, setChartData] = useState([]);

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
      text: '처리육 관능데이터 박스 플롯(Box Plot) 분포',
    },
  };

  // Conditionally render the chart only when chartData is not empty
  return (
    <div>
      {chartData && chartData.color && chartData.color.values ? (
        <ApexCharts
          series={[
            {
              type: 'boxPlot',
              data: [
                {
                  x: '색(Color)',
                  y: calculateBoxPlotStatistics(chartData.color.values),
                },
                {
                  x: '마블링(Marbling)',
                  y: calculateBoxPlotStatistics(chartData.marbling.values),
                },
                {
                  x: '기호도(Overall)',
                  y: calculateBoxPlotStatistics(chartData.overall.values),
                },
                {
                  x: '육즙(SurfaceMoisture)',
                  y: calculateBoxPlotStatistics(
                    chartData.surfaceMoisture.values
                  ),
                },
                {
                  x: '조직감(Texture)',
                  y: calculateBoxPlotStatistics(chartData.texture.values),
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

export default Sens_ProcMeat;
