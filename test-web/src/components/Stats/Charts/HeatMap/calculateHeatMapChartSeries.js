function calculateHeatMapChartSeries(prop, chartData, y_axis) {
    return prop
      .map((property) => {
        const uniqueValues = chartData[property].values;
        const frequencies = new Array(11).fill(0);
  
        uniqueValues.forEach((value) => {
          if (value > 10) {
            frequencies[10] += 1;
          } else if (value < 1) {
            frequencies[0] += 1;
          } else {
            const index = Math.floor(value);
            frequencies[index] += 1;
          }
        });
  
        return {
          name: y_axis[property] || property,
          data: frequencies,
        };
      })
      .reverse();
  }
  
export default calculateHeatMapChartSeries