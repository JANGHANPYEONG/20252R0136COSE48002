import React, { useEffect, useState } from 'react';
import ApexCharts from 'react-apexcharts';
import CircularProgress from '@mui/material/CircularProgress';
import { statisticSensoryFresh } from '../../../../API/statistic/statisticSensoryFresh';
import { statisticSensoryProcessed } from '../../../../API/statistic/statisticSensoryProcessed';
import { statisticSensoryHeated } from '../../../../API/statistic/statisticSensoryHeated';
import { statisticProbexptFresh } from '../../../../API/statistic/statisticProbexptFresh';
import { statisticProbexptProcessed } from '../../../../API/statistic/statisticProbexptProcessed';
import calculateBoxPlotStatistics from './calculateBoxPlotStat';
import axisLabels from '../constants/axisLabels';

const BoxPlotChart = ({
  meatState,
  dataType,
  startDate,
  endDate,
  animalType,
  grade,
}) => {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        let response;
        if (meatState === '원육' && dataType === 'sensory') {
          response = await statisticSensoryFresh(
            startDate,
            endDate,
            animalType,
            grade
          );
        } else if (meatState === '처리육' && dataType === 'sensory') {
          response = await statisticSensoryProcessed(
            startDate,
            endDate,
            animalType,
            grade
          );
        } else if (meatState === '가열육' && dataType === 'sensory') {
          response = await statisticSensoryHeated(
            startDate,
            endDate,
            animalType,
            grade
          );
        } else if (meatState === '원육' && dataType === 'taste') {
          response = await statisticProbexptFresh(
            startDate,
            endDate,
            animalType,
            grade
          );
        } else if (meatState === '처리육' && dataType === 'taste') {
          response = await statisticProbexptProcessed(
            startDate,
            endDate,
            animalType,
            grade
          );
        } else {
          throw new Error('Invalid meat state or data type');
        }

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
  }, [startDate, endDate, animalType, grade, meatState, dataType]);

  const chartOptions = {
    chart: {
      type: 'boxPlot',
      height: 350,
    },
    title: {
      text: `${meatState} ${dataType === 'sensory' ? '관능' : '맛'}데이터 박스 플롯(Box Plot) 분포`,
    },
  };

  const currentLabels = axisLabels[dataType][meatState] || {};

  const renderChart = () => {
    if (
      !chartData ||
      !currentLabels ||
      Object.keys(currentLabels).length === 0
    ) {
      return <CircularProgress />;
    }

    const series = [
      {
        type: 'boxPlot',
        data: Object.entries(currentLabels).map(([key, value]) => ({
          x: `${value}(${key})`,
          y: calculateBoxPlotStatistics(chartData[key].values),
        })),
      },
    ];

    return (
      <ApexCharts
        series={series}
        options={chartOptions}
        type="boxPlot"
        height={350}
      />
    );
  };

  return <div>{renderChart()}</div>;
};

export default BoxPlotChart;
