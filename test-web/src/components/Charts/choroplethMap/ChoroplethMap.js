import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useMapFetch } from '../../../API/listCharts/getChoroplethMapSWR';

const ChoroplethMap = ({ mapData, startDate, endDate }) => {
  const [keyIdx, setKeyIdx] = useState(0);
  // fetch한 지역별 개수 API 데이터 저장
  const [geoJSONData, setGeoJSONData] = useState(mapData);

  // geoJSON 데이터 properites 추가 함수
  /**
   *  [{properties: 
      {value : 
            {cattle : '소의 데이터 개수', 
             pork : '돼지의 데이터 개수', 
             total : '전체 데이터 개수' }
       }}, 
     ... ] 형태로 geoJSON 데이터 업테이트
  */
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

    // geoJSONData에 저장
    setGeoJSONData(updatedGeoJSON);
  };

  // fetch한 JSON 데이터 전처리
  const processMapData = (data) => {
    // fetch한 JSON 데이터 parsing
    const cattleCnt = data['cattle_counts_by_region'];
    const porkCnt = data['pig_counts_by_region'];
    const totalCnt = data['total_counts_by_region'];
    // geoJSON 데이터에 properties 추가
    addProperties(cattleCnt, porkCnt, totalCnt);
    setKeyIdx((prev) => prev + 1);
  };

  // 지역 별 개수 데이터 API fetch
  const { data, isLoading, isError } = useMapFetch(startDate, endDate);
  console.log('map fetch 결과:', data);

  // fetch한 JSON 데이터 전처리 함수 call
  useEffect(() => {
    if (data !== null && data !== undefined) {
      processMapData(data);
    }
  }, [data]);

  // 지역별 개수에 따른 색 설정
  const getColor = (value) => {
    if (!value) {
      return '#ffffff';
    }
    const cattle = value.cattle;
    const pork = value.pork;
    const total = value.total;
    if (total === 0) {
      // 데이터가 없는 경우
      return '#ffffff';
    } else if (cattle === 0 && pork) {
      // 돼지 데이터만 있는 경우
      return pork > 40
        ? '#e91e63'
        : pork > 30
          ? '#ec407a'
          : pork > 20
            ? '#f06292'
            : pork > 10
              ? '#f48fb1'
              : '#f8bbd0';
    } else if (cattle && pork === 0) {
      // 소 데이터만 있는 경우
      return cattle > 40
        ? '#2196f3'
        : cattle > 30
          ? '#42a5f5'
          : cattle > 20
            ? '#64b5f6'
            : cattle > 10
              ? '#90caf9'
              : '#bbdefb';
    } else {
      // 둘다 있는 경우
      return total > 40
        ? '#9c27b0'
        : total > 30
          ? '#ab47bc'
          : total > 20
            ? '#ba68c8'
            : total > 10
              ? '#ce93d8'
              : '#e1bee7';
    }
  };

  //지도 스타일
  const style = (features) => {
    const value = features.properties.value;
    return {
      fillColor: getColor(value),
      weight: 1,
      opacity: 1,
      color: 'black', // 선 색깔
      fillOpacity: 0.9,
    };
  };

  //state(지역) layer에 listener(설명) 추가
  const onEachFeature = (feature, layer) => {
    if (feature.properties.value) {
      // value가 있는 경우 다음 pop-up을 bind
      /**
       * "지역:'지역 이름', 전체:'전체 데이터 개수', 소:'소 데이터 개수', 돼지: '돼지 데이터 개수' "
       */
      layer.bindPopup(`
          지역: ${feature.properties.CTP_KOR_NM}<br>
          전체: ${feature.properties.value.total ? feature.properties.value.total : 0} 마리<br>
          소: ${feature.properties.value.cattle ? feature.properties.value.cattle : 0} 마리<br>
          돼지: ${feature.properties.value.pork ? feature.properties.value.pork : 0} 마리
        `);
    }
    // value가 있는 경우 다음 pop-up을 bind
    /**
     * "지역:'지역 이름'"
     */
    else layer.bindPopup(`지역: ${feature.properties.CTP_KOR_NM}`);
  };

  return (
    <MapContainer
      center={[35.8754, 128.5823]} //center: 지도의 initial center를 설정 center={['위도', '경도']}.
      style={{ height: '350px' }} //style: map container의 높이를 설정
      zoom={6} //zoom: initial zoom level을 설정
      scrollWheelZoom={false} //scrollWheelZoom: 스크롤 wheel로 zooming 하는 것을 막기
    >
      {/*Add a TileLayer component to display the map tiles. */}
      <TileLayer
        style={styles.customTileLayer}
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {/*Add a GeoJSON layer to display geographical features on the map. */}
      {/**
         * - key: Unique key for GeoJSON layer (keyIdx).
          - data: GeoJSON data to be displayed on the map.
          - style: Styling options for the GeoJSON features.
          - onEachFeature: Function to be called for each feature in the GeoJSON layer.
         */}
      <GeoJSON
        key={keyIdx}
        data={geoJSONData}
        style={style}
        onEachFeature={onEachFeature}
      />
    </MapContainer>
  );
};

export default ChoroplethMap;

const styles = {
  customTileLayer: {
    border: '5px solid #ccc',
    borderRadius: '4px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
};
