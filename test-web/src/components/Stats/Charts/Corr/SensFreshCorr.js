import React, { useEffect, useState } from 'react';
import ApexCharts from 'react-apexcharts';
import { statisticSensoryFresh } from '../../../../API/statistic/statisticSensoryFresh';
import calculateCorrChartSeries from './calculateCorrChartSeries';
import getCorrChartOption from './getCorrChartOption';

const SenseFreshCorr = ({ startDate, endDate, animalType, grade }) => {
  const [chartData, setChartData] = useState({});
  const [prop, setProp] = useState([]);

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
        setProp(Object.keys(data));
        setChartData(data);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, [startDate, endDate, animalType, grade]);

  const axis_labels = {
    color: '색',
    marbling: '마블링',
    overall: '기호도',
    surfaceMoisture: '육즙',
    texture: '조직감',
  };

  const ChartSeries = calculateCorrChartSeries(prop, chartData, axis_labels);

  const xCategories = prop
    .slice()
    .reverse()
    .map((p) => axis_labels[p] || p);

  const ChartOption = {
    ...getCorrChartOption(xCategories),
    title: {
      text: '원육 관능데이터 상관관계',
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

export default SenseFreshCorr;
