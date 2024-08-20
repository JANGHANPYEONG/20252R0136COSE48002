import React, { useEffect, useState } from 'react';
import ApexCharts from 'react-apexcharts';
import { statisticProbexptProcessed } from '../../../../API/statistic/statisticProbexptProcessed';
import calculateCorrChartSeries from './calculateCorrChartSeries';
import getCorrChartOption from './getCorrChartOption';

const TasteProcCorr = ({ startDate, endDate, animalType, grade }) => {
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

  const axis_labels = {
    bitterness: '진한맛',
    richness: '후미',
    sourness: '신맛',
    umami: '감칠맛',
  };

  const ChartSeries = calculateCorrChartSeries(prop, chartData, axis_labels);

  const xCategories = prop
    .slice()
    .reverse()
    .map((p) => axis_labels[p] || p);

  const ChartOption = {
    ...getCorrChartOption(xCategories),
    title: {
      text: '처리육 맛데이터 상관관계',
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

export default TasteProcCorr;
