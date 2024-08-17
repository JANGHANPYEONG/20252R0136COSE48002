import ApexCharts from 'react-apexcharts';
import React, { useEffect, useState } from 'react';
import { statisticProbexptProcessed } from '../../../../API/statistic/statisticProbexptProcessed';
import calculateHeatMapChartSeries from './calculateHeatMapChartSeries';
import getHeatMapChartOption from './getHeatMapChartOption';

const TasteProcMap = ({ startDate, endDate, animalType, grade }) => {
  const [chartData, setChartData] = useState({});
  const [prop, setProp] = useState([]);

  useEffect(() => {
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
        setProp(Object.keys(data));
        setChartData(data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [startDate, endDate, animalType, grade]);

  const y_axis = {
    bitterness: '진한맛',
    richness: '후미',
    sourness: '신맛',
    umami: '감칠맛',
  };

  const ChartSeries = calculateHeatMapChartSeries(prop, chartData, y_axis);
  const ChartOption = {
    ...getHeatMapChartOption(ChartSeries, y_axis),
    title: {
      text: '처리육 맛데이터 범위별 분포(빈도수)',
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

export default TasteProcMap;
