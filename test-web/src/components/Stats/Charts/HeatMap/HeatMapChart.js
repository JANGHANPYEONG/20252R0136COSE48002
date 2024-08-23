import React, { useEffect, useState } from 'react';
import ApexCharts from 'react-apexcharts';
import { statisticSensoryFresh } from '../../../../API/statistic/statisticSensoryFresh';
import { statisticSensoryProcessed } from '../../../../API/statistic/statisticSensoryProcessed';
import { statisticSensoryHeated } from '../../../../API/statistic/statisticSensoryHeated';
import { statisticProbexptFresh } from '../../../../API/statistic/statisticProbexptFresh';
import { statisticProbexptProcessed } from '../../../../API/statistic/statisticProbexptProcessed';
import calculateHeatMapChartSeries from './calculateHeatMapChartSeries';
import getHeatMapChartOption from './getHeatMapChartOption';
import axisLabels from '../constants/axisLabels';

const HeatMapChart = ({
  meatState,
  dataType,
  startDate,
  endDate,
  animalType,
  grade,
}) => {
  const [chartData, setChartData] = useState({});
  const [prop, setProp] = useState([]);

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
        setProp(Object.keys(data));
        setChartData(data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [startDate, endDate, animalType, grade, meatState, dataType]);

  const currentYAxis = axisLabels[dataType][meatState] || {};

  const ChartSeries = calculateHeatMapChartSeries(
    prop,
    chartData,
    currentYAxis
  );

  const ChartOption = {
    ...getHeatMapChartOption(ChartSeries, currentYAxis),
    title: {
      text: `${meatState} ${dataType === 'sensory' ? '관능' : '맛'}데이터 범위별 분포(빈도수)`,
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
};

export default HeatMapChart;
