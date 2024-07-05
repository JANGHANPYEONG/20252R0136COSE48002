import geojsonData from './geojson_korea.json';
import ChoroplethMap from './ChoroplethMap';

function Map({ startDate, endDate }) {
  // ChoropletMap 컴포넌트를 반환
  return (
    <div style={{ width: '350px', height: '350px' }}>
      <ChoroplethMap
        mapData={geojsonData}
        startDate={startDate}
        endDate={endDate}
      />
    </div>
  );
}

export default Map;
