import { useState, useEffect } from 'react';
import DataView from './DataView';
import DataPAView from './DataPAView';
import DataConfirmView from './DataConfirmView';
import dataProcessing from './dataProcessing';
import Spinner from 'react-bootstrap/Spinner';
import { useDetailMeatData } from '../../API/get/getDetailMeatDataSWR';

//하나의 관리번호에 대한 육류 상세 데이터를 API로 부터 fetch
const DataLoad = ({ id, page }) => {
  // 전처리된 상세 데이터 저장
  const [detailData, setDetailData] = useState();

  // 육류 상세 데이터 API fetch
  const { data, isLoading, isError } = useDetailMeatData(id);


  //데이터 전처리
  useEffect(() => {
    if (data !== null && data !== undefined) {
      setDetailData(dataProcessing(data));
    }
  }, [data]);

  if (data === null) return null;
  if (isLoading)
    return (
      // 데이터가 로드되지 않은 경우 로딩중 반환
      <div>
        <Spinner animation="border" />
      </div>
    );
  if (isError) return null; //경고 컴포넌트

  return (
    <>
      {detailData !== undefined &&
        (page === '예측' ? (
          <DataPAView dataProps={detailData} />
        ) : page === '수정및조회' ? (
          <DataView dataProps={detailData} />
        ) : (
          page === '검토' && <DataConfirmView dataProps={detailData} />
        ))}
    </>
  );
};

export default DataLoad;
