import DataList from './DataList';
import style from './style/pasinglestyle';

// 데이터 목록 조회 페이지 컴포넌트
const PASingle = ({ startDate, endDate, singleData }) => {
  // 현재 페이지 번호
  const currentPage = 1;
  // 한 페이지당 보여줄 개수
  const count = 5;
  let meatData = [singleData];

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
