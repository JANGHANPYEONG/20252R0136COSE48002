const calculateBoxPlotStatistics = (data) => {
  const sortedData = data.sort((a, b) => a - b);
  const q1Index = Math.floor(sortedData.length / 4);
  const medianIndex = Math.floor(sortedData.length / 2);
  const q3Index = Math.floor((3 * sortedData.length) / 4);

  const q1 = sortedData[q1Index];
  const median = sortedData[medianIndex];
  const q3 = sortedData[q3Index];
  const min = sortedData[0];
  const max = sortedData[sortedData.length - 1];
  return [min, q1, median, q3, max];
};
export default calculateBoxPlotStatistics;
