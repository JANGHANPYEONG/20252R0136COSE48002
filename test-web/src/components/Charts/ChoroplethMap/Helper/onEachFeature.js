const onEachFeature = (feature, layer) => {
    if (feature.properties.value) {
      layer.bindPopup(`
          지역: ${feature.properties.CTP_KOR_NM}<br>
          전체: ${feature.properties.value.total ? feature.properties.value.total : 0} 마리<br>
          소: ${feature.properties.value.cattle ? feature.properties.value.cattle : 0} 마리<br>
          돼지: ${feature.properties.value.pork ? feature.properties.value.pork : 0} 마리
        `);
    } else {
      layer.bindPopup(`지역: ${feature.properties.CTP_KOR_NM}`);
    }
  };

export default onEachFeature