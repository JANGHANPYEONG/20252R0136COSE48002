  // 토글 버튼 handle (전체, 소, 돼지)
  const handleBtnClick = (e, setLabel, setChartSeries, data) => {
    const value = e.target.value;
    let newChartSeries = [-1, -1]; // 기본값으로 [-1, -1]을 설정

    if (data && data !== null && data !== undefined && value in data) {
      const categoryData = data[value];
      if (
        categoryData &&
        'raw' in categoryData &&
        'processed' in categoryData
      ) {
        const raw = categoryData.raw;
        const processed = categoryData.processed;

        newChartSeries = [
          !Number.isNaN(raw) ? raw : -1,
          !Number.isNaN(processed) ? processed : -1,
        ];
      }
    } else {
      console.log('Invalid data structure:', value);
    }

    setLabel(value);
    setChartSeries(newChartSeries);
  };

  export default handleBtnClick