import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import { statisticSensoryProcessed } from '../../../../API/statistic/statisticSensoryProcessed';
import calculateHeatMapChartSeries from './calculateHeatMapChartSeries';
import getHeatMapChartOption from './getHeatMapChartOption';

const SensProcMap = ({ startDate, endDate, animalType, grade }) => {
  const [chartData, setChartData] = useState({});
  const [prop, setProp] = useState([]);

  useEffect(() => {
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
        setProp(Object.keys(data));
        setChartData(data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [startDate, endDate, animalType, grade]);

  const y_axis = {
    color: '색',
    marbling: '마블링',
    overall: '기호도',
    surfaceMoisture: '육즙',
    texture: '조직감',
  };

  const ChartSeries = calculateHeatMapChartSeries(prop, chartData, y_axis);
  const ChartOption = {
    ...getHeatMapChartOption(ChartSeries, y_axis),
    title: {
      text: '처리육 관능데이터 범위별 분포(빈도수)',
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

export default SensProcMap;
