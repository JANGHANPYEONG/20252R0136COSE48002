import React, { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import Spinner from 'react-bootstrap/Spinner';
import DataList from './DataList';
import style from './style/searcheddatastyle';

const SearchedDataListComp = ({ startDate, endDate, searchedData }) => {
  const [meatList, setMeatList] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  // API fetch 데이터 전처리
  const processMeatData = (data) => {
    if (!data) {
      console.error('올바르지 않은 데이터 형식:', data);
      return;
    }

    // 검색 결과가 여러 개인 경우 (partial search)
    if (data.meat_dict && data.id_list) {
      let processedData = [];
      data.id_list.forEach((id) => {
        if (data.meat_dict[id]) {
          processedData = [...processedData, data.meat_dict[id]];
        }
      });
      setMeatList(processedData);
    }
    // 단일 검색 결과인 경우
    else {
      setMeatList([data]);
    }
  };

  useEffect(() => {
    setIsLoading(true);
    if (searchedData) {
      processMeatData(searchedData);
    }
    setIsLoading(false);
  }, [searchedData]);

  if (isLoading) {
    return (
      <div style={style.listContainer}>
        <Spinner animation="border" />
      </div>
    );
  }

  return (
    <div>
      <div style={style.listContainer}>
        {meatList.length > 0 ? (
          <DataList
            meatList={meatList}
            pageProp={'list'} // 육류 목록 페이지임을 명시
            offset={0}
            count={meatList.length}
            startDate={startDate}
            endDate={endDate}
            pageOffset={0}
          />
        ) : (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '200px',
              fontSize: '1.2rem',
              color: '#666',
            }}
          >
            검색 결과가 없습니다.
          </Box>
        )}
      </div>
    </div>
  );
};

export default SearchedDataListComp;
