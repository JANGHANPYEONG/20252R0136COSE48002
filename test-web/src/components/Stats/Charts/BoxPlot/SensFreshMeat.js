import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import CircularProgress from '@mui/material/CircularProgress';
import { statisticSensoryFresh } from '../../../../API/statistic/statisticSensoryFresh';
import calculateBoxPlotStatistics from './calculateBoxPlotStat';

const SensFreshMeat = ({ startDate, endDate, animalType, grade }) => {
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await statisticSensoryFresh(
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

    fetchData();
  }, [startDate, endDate, animalType, grade]);

  const chartOptions = {
    chart: {
      type: 'boxPlot',
      height: 350,
    },
    title: {
      text: '원육 관능데이터 박스 플롯(Box Plot) 분포',
    },
    // plotOptions: {
    //   boxPlot: {
    //     colors: {
    //       upper: '#7BD758',
    //       lower: '#BFE692',
    //     },
    //   },
    // },
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

export default SensFreshMeat;
