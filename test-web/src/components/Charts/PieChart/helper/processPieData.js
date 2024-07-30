  // fetch한 JSON 데이터에서 필요한 값 parsing 및 chartSeries에 저장
  // 렌더링 시 데이터 받지 못하면 -1, -1
  const processPieData = (data, setChartSeries) => {
    if (
      data &&
      'total_counts' in data &&
      'raw' in data.total_counts &&
      'processed' in data.total_counts
    ) {
      const raw = data.total_counts.raw;
      const processed = data.total_counts.processed;

      setChartSeries([
        !Number.isNaN(raw) ? raw : -1,
        !Number.isNaN(processed) ? processed : -1,
      ]);
    } else {
      console.log('Invalid data structure:', data);
      setChartSeries([-1, -1]); // Default to [-1, -1] if data is invalid
    }
  };

  export default processPieData