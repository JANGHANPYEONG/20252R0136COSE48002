export const processMapData = (data, mapData, setGeoJSONData, setKeyIdx) => {
  if (
    !data['cattle_counts_by_region'] ||
    !data['pig_counts_by_region'] ||
    !data['total_counts_by_region']
  ) {
    console.error('올바르지 않은 데이터 형식:', data);
    return;
  }

  // fetch한 JSON의 지역 데이터명을 geoJSON 데이터에 맞게 수정
  const renameRegions = (region) => {
    const regionMap = {
      경상남: '경남',
      경상북: '경북',
      충청남: '충남',
      충청북: '충북',
      전라남: '전남',
      전라북: '전북',
    };
    return regionMap[region] || region;
  };

  const renamedData = (obj) => {
    const newObj = {};
    for (const key in obj) {
      newObj[renameRegions(key)] = obj[key];
    }
    return newObj;
  };

  const cattleCnt = renamedData(data['cattle_counts_by_region']);
  const porkCnt = renamedData(data['pig_counts_by_region']);
  const totalCnt = renamedData(data['total_counts_by_region']);

  // geoJSON 데이터에 properties 추가
  const addProperties = (cattleCnt, porkCnt, totalCnt) => {
    const updatedFeatures = mapData.features.map((feature) => ({
      ...feature,
      properties: {
        ...feature.properties,
        value: {
          cattle: cattleCnt[feature.properties.CTP_KOR_NM],
          pork: porkCnt[feature.properties.CTP_KOR_NM],
          total: totalCnt[feature.properties.CTP_KOR_NM],
        },
      },
    }));

    const updatedGeoJSON = {
      ...mapData,
      features: updatedFeatures,
    };

    setGeoJSONData(updatedGeoJSON);
  };

  addProperties(cattleCnt, porkCnt, totalCnt);
  setKeyIdx((prev) => prev + 1);
};
export default processMapData;
