import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useStatisticChoroplethMap } from '../../../API/statistic/statsticChoroplethMapSWR';
import { processMapData } from './helper/processMapData'; // processMapData 함수를 import
import getColor from './helper/getColor';
import onEachFeature from './helper/onEachFeature';

const ChoroplethMap = ({ mapData, startDate, endDate }) => {
  const [keyIdx, setKeyIdx] = useState(0);
  const [geoJSONData, setGeoJSONData] = useState(mapData);

  //API fetching
  const { data, isLoading, isError } = useStatisticChoroplethMap(
    startDate,
    endDate
  );

  //지역 데이터명 수정, properties 추가
  useEffect(() => {
    if (data !== null && data !== undefined) {
      processMapData(data, mapData, setGeoJSONData, setKeyIdx);
    }
  }, [data]);

  const style = (features) => {
    const value = features.properties.value;
    return {
      fillColor: getColor(value),
      weight: 1,
      opacity: 1,
      color: 'black',
      fillOpacity: 0.9,
    };
  };

  return (
    <MapContainer
      center={[35.8754, 128.5823]}
      style={{ height: '350px' }}
      zoom={6}
      scrollWheelZoom={true}
    >
      <TileLayer
        style={styles.customTileLayer}
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <GeoJSON
        key={keyIdx}
        data={geoJSONData}
        style={style}
        onEachFeature={onEachFeature}
      />
    </MapContainer>
  );
};

const styles = {
  customTileLayer: {
    border: '5px solid #ccc',
    borderRadius: '4px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
};

export default ChoroplethMap;
