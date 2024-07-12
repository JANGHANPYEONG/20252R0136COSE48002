import { useState, useEffect } from 'react';
import DataList from './DataList';


// 데이터 목록 조회 페이지 컴포넌트
const PASingle = ({ startDate, endDate, data }) => {
  // 현재 페이지 번호
  const [currentPage, setCurrentPage] = useState(1);
  // 한 페이지당 보여줄 개수
  const [count, setCount] = useState(5);
  let meatData = [data];

  return (
    <div>
      <div style={style.listContainer}>
        {meatData !== undefined && (
          <DataList
            meatList={meatData}
            pageProp={'pa'} // 육류 목록 페이지임을 명시
            offset={currentPage - 1}
            count={count}
            startDate={startDate}
            endDate={endDate}
            pageOffset={0}
          />
        )}
      </div>
    </div>
  );
};

export default PASingle;

const style = {
  listContainer: {
    textAlign: 'center',
    width: '100%',
    paddingRight: '0px',
    paddingBottom: '0',
    height: 'auto',
  },
  paginationBar: {
    marginTop: '40px',
    width: '100%',
    justifyContent: 'center',
  },
  paginationContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  formControl: {
    minWidth: 120,
    marginLeft: '20px',
  },
};
