import React, { useEffect, useState } from 'react';
import ApexCharts from 'react-apexcharts';
import { statisticProbexptFresh } from '../../../../API/statistic/statisticProbexptFresh';
import calculateCorrChartSeries from './calculateCorrChartSeries';
import getCorrChartOption from './getCorrChartOption';

const TasteFreshCorr = ({ startDate, endDate, animalType, grade }) => {
  const [chartData, setChartData] = useState({});
  const [prop, setProp] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await statisticProbexptFresh(
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

  // 두 배열의 상관 관계 계수 계산

  const xCategories = prop
    .slice()
    .reverse()
    .map((p) => axis_labels[p] || p);

  const ChartOption = {
    ...getCorrChartOption(xCategories),
    title: {
      text: '원육 맛데이터 상관관계',
    },
  };

  return (
    <ApexCharts
      options={ChartOption}
      series={ChartSeries}
      type="heatmap"
      width="100%"
      height={350}
    />
  );
};

export default TasteFreshCorr;
