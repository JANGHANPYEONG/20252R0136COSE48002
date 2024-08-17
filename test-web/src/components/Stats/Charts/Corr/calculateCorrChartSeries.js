import calculateCorrelation from './calculateCorrelation';

const calculateCorrChartSeries = (prop, chartData, axis_labels) => {
  const propArray = Array.isArray(prop) ? prop : [];

  return propArray
    .map((property, rowIndex) => {
      const uniqueValues1 = chartData[property]?.values || [];
      const correlation = new Array(prop.length).fill(0);

      for (let colIndex = 0; colIndex < prop.length; colIndex++) {
        if (colIndex === rowIndex) {
          correlation[colIndex] = 100; // 대각선 위치는 1로 설정
        } else {
          const uniqueValues2 = chartData[prop[colIndex]]?.values || [];

          // 상관 관계 계수 계산
          const correlationCoefficient = calculateCorrelation(
            uniqueValues1,
            uniqueValues2
          );

          correlation[colIndex] = correlationCoefficient;
        }
      }

      return {
        name: axis_labels[property] || property,
        data: correlation.reverse(),
      };
    })
    .reverse();
};

export default calculateCorrChartSeries;
