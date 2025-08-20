import { useState, useEffect, useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
// mui
import { Box, Button, Select, MenuItem, CircularProgress, Typography } from '@mui/material';
// style
import style from './style/dashboardstyle';
// icon, timezone
import { FaBoxOpen } from 'react-icons/fa';
import { TIME_ZONE } from '../config';
// 검색 필터 컴포넌트
import SearchFilterBar from '../components/Search/SearchFilterBar';
// 육류 목록 컴포넌트
import DataListComp from '../components/DataListView/DataListComp';
// 목록 현황 컴포넌트
import DataStat from '../components/Charts/DataStat';
// 반려 데이터 목록 컴포넌트
import RejectedDataListComp from '../components/DataListView/RejectedDataListComp';
// 엑셀 파일 export/ import 컴포넌트
import ExcelController from '../components/DataListView/ExcelController';
// import StatsExport from '../components/DataListView/StatsExport_';
// ID 검색 컴포넌트
import SearchById from '../components/DataListView/SearchById';
import SearchedDataListComp from '../components/DataListView/SearchedDataListComp';
// 구간 계산 함수
import updateDates from '../Utils/updateDates';

// temp for mocking
import PredictionTableTmp from '../components/PredictionTableTmp';
import FilterModal from '../components/FilterModal';
import PredictionTable from '../components/PredictionTable';
import PredictionDetailPanel from '../components/PredictionDetailPanel';
import { fetchFilteredData } from '../API/fetchFileteredData';
import { Snackbar, Alert } from '@mui/material';
import { fetchPrediction } from '../API/predictData';
import ExportSelectedToExcel from '../components/ExportSelectedToExcel';
//////////////////////////////////////////////////

const navy = '#0F3659';

const OldDashboard = () => {
  const [value, setValue] = useState('list');
  const [specieValue, setSpecieValue] = useState('전체');
  const [searchedData, setSearchedData] = useState(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [pageOffset, setPageOffset] = useState(1);
  const [isLoading, setIsLoading] = useState(true);


  // temp for mocking
  const [groupedData, setGroupedData] = useState([]);
  const [selectedRows, setSelectedRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterModalOpen, setFilterModalOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, severity: 'info', message: '완료' });

  const [openPanel, setOpenPanel] = useState(false);
  const [detailData, setDetailData] = useState(null);
  const [filters, setFilters] = useState([
    { name: '날짜', type: 'date', options: [], value: { start: null, end: null } },
  ]);
  const [data, setData] = useState([]);
  const navigate = useNavigate();
  //////////////////////////////////////////////////
  // 쿼리스트링 추출
  const location = useLocation();
  const { querypageOffset, queryStartDate, queryEndDate, queryDuration, queryTab } =
    useMemo(() => {
      const searchParams = new URLSearchParams(location.search);
      return {
        querypageOffset: searchParams.get('pageOffset'),
        queryStartDate: searchParams.get('start') || '',
        queryEndDate: searchParams.get('end') || '',
        queryDuration: searchParams.get('duration') || '',
        queryTab: searchParams.get('tab') || '',
      };
    }, [location.search]);

  useEffect(() => {
    setPageOffset(querypageOffset);
  }, [querypageOffset]);

  // URL의 tab 쿼리 파라미터로 초기 탭 선택 (예: /NewDashboard?tab=reject)
  useEffect(() => {
    if (queryTab) {
      setValue(queryTab);
    }
  }, [queryTab]);

  useEffect(() => {
    setIsLoading(true);
    const now = new Date();
    let start = new Date('1970-01-01T00:00:00Z');
    let end = new Date(now);

    if (queryDuration) {
      const { start: durationStart, end: durationEnd } =
        updateDates(queryDuration);
      start = new Date(durationStart);
      end = new Date(durationEnd);
    } else if (queryStartDate || queryEndDate) {
      // startDate 또는 endDate 파라미터가 있을 경우
      if (queryStartDate) {
        start = new Date(queryStartDate);
      }
      if (queryEndDate) {
        end = new Date(queryEndDate);
      }
    } else {
      // 기본값 설정 (1년 전부터 현재까지)
      start = new Date(now);
      start.setFullYear(now.getFullYear() - 1);
    }

    const formattedStartDate = new Date(start.getTime() + TIME_ZONE)
      .toISOString()
      .slice(0, -5);
    const formattedEndDate = new Date(end.getTime() + TIME_ZONE)
      .toISOString()
      .slice(0, -5);

    setStartDate(formattedStartDate);
    setEndDate(formattedEndDate);
    setIsLoading(false);
  }, [queryStartDate, queryEndDate, queryDuration, location.search]);

  const handleValueChange = (newValue) => {
    setValue(newValue);
  };

  const handleSpeciesChange = (event) => {
    setSpecieValue(event.target.value);
  };

  const handleSearchedDataFetch = (fetchedData) => {
    setSearchedData(fetchedData);
  };

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }
// temp for mocking
  // 예측 페이지로 이동
  const goLearningPage = () => {
    const selectedSet = new Set(
      selectedRows.map((s) => (typeof s === 'string' ? s : s.id))
    );
    const payload =
      selectedRows.length > 0
        ? data.filter((row) => selectedSet.has(row.id))
        : data;
    // 새로고침 대비 백업(옵션)
    try {
      sessionStorage.setItem('predict_data', JSON.stringify(payload));
    } catch {}

    navigate('/Learning', { state: { data: payload, selectedRows: selectedRows, from: 'dashboard' } });
  };
  const goPredictPage = () => {
    const selectedSet = new Set(
      selectedRows.map((s) => (typeof s === 'string' ? s : s.id))
    );
    const payload =
      selectedRows.length > 0
        ? data.filter((row) => selectedSet.has(row.id))
        : data;
    // 새로고침 대비 백업(옵션)
    try {
      sessionStorage.setItem('predict_data', JSON.stringify(payload));
    } catch {}

    navigate('/predict', { state: { data: payload, selectedRows: selectedRows, from: 'dashboard' } });
  };
  // 데이터 불러오기 함수
  const handleLoadData = async () => {
    setLoading(true);
    // 실제 API 호출 로직이 여기에 들어갈 예정
    // 필터 옵현 추가해야함
    try {
      const result = await fetchFilteredData(filters, value);
      setData(result);
      // upload_batch_id 기준으로 그룹핑
      const groupMap = {};
      result.forEach((item) => {
        const batchId = item.upload_batch_id || 'unknown_batch';
        if (!groupMap[batchId]) groupMap[batchId] = [];
        groupMap[batchId].push(item);
      });
      const grouped = Object.entries(groupMap).map(([batchId, rows]) => ({
        batchId,
        timestamp: rows[0]?.timestamp || '',
        rows,
      }));

      setGroupedData(grouped);
      // 성공 여부 알림
      setSnackbar({
        open : true,
        severity: 'success',
        message: `데이터 ${result.length}개를 성공적으로 불러왔습니다.`,
      });
    } catch (err) {
      console.error('데이터 불러오기 실패:', err);
      setSnackbar({
        open : true,
        severity: 'error',
        message: '데이터 불러오기 실패! 서버를 확인해주세요.',
      });
    }
    setLoading(false)
  };

  // 선택 변경 핸들러
  const handleSelectionChange = (newSelection) => {
    setSelectedRows(newSelection);
  };

  // Rowclick 여부 다루기
  const handleRowClick = (row) => {
    if (!row.prediction) return;
    setDetailData({ id: row.id, prediction: row.prediction, sensory: row.sensory});
    setOpenPanel(true);
  };

  // 선택된 데이터 predict하기
  const handlePredict = async () => {
    // if (selectedRows.length ===0) {
    //   setSnackbar({ open: true, severity: 'warning', message:'예측할 데이터를 선택해주세요.'});
    //   return;
    // }
    setLoading(true);
    try {
      const result = await fetchPrediction(selectedRows); // { id : 예측하고 할(선택된) 값들}
      const newData = data.map(row => (
        result[row.id] ? { ...row, prediction: result[row.id] } : row
      ));
      setData(newData);
      setSnackbar({  open: true, severity: 'success', message: '예측 성공!'});
    } catch (err) {
      setSnackbar({ open: true, severity: 'error', message: '예측 실패! 서버 상태를 확인해주세요.' });
    }
    setLoading(false);
  }
  // 필터 함수
  const handleFilter = () => {
    setFilterModalOpen(true);
  };

  const initializeData = () => {
    setData([]);
  }
  // 필터 적용 함수
  const handleApplyFilters = (appliedFilters) => {
    setFilters(appliedFilters);
    console.log('적용된 필터:', appliedFilters);
    // 여기서 필터링된 데이터를 API로 요청
    handleLoadData(); // 필터 적용 후 데이터 다시 로드
  };
////////////////////////////////////////////////////////



  return (
    <div
      style={{
        overflow: 'auto',
        width: '100%',
        marginTop: '100px',
        height: '100%',
        paddingLeft: '30px',
        paddingRight: '20px',
      }}
    >
      {/**페이지 제목 Dashboard ()> 반려함) */}
      <Box
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          minWidth: '634px', // minimum width
        }}
      >
        {value === 'reject' ? (
          <div style={{ display: 'flex' }}>
            <span
              style={{ color: '#b0bec5', fontSize: '30px', fontWeight: '600' }}
            >
              Dashboard {'>'}{' '}
            </span>
            <span
              style={{ color: `${navy}`, fontSize: '30px', fontWeight: '600' }}
            >
              반려함
            </span>
          </div>
        ) : (
          <span
            style={{ color: `${navy}`, fontSize: '30px', fontWeight: '600' }}
          >
            Dashboard
          </span>
        )}

        <div style={{ display: 'flex', justifyContent: 'end' }}>
          <Button
            style={
              value === 'reject'
                ? style.tabBtnCilcked
                : { color: `${navy}`, border: `1px solid ${navy}` }
            }
            value="reject"
            variant="outlined"
            onClick={(e) => {
              setValue(e.target.value);
            }}
          >
            <FaBoxOpen style={{ marginRight: '3px' }} />
            반려함
          </Button>
        </div>
      </Box>

      {/**이동 탭 (목록, 통계 , 반려) */}
      <Box sx={style.fixedTab}>
        <div style={{ display: 'flex' }}>
          <Button
            style={value === 'list' ? style.tabBtnCilcked : style.tabBtn}
            value="list"
            variant="outlined"
            onClick={(e) => {
              setValue(e.target.value);
            }}
          >
            목록
          </Button>
          {value !== 'searched' && (
            <Button
              style={value === 'stat' ? style.tabBtnCilcked : style.tabBtn}
              value="stat"
              variant="outlined"
              onClick={(e) => {
                setValue(e.target.value);
              }}
            >
              현황
            </Button>
          )}
        </div>
      </Box>
      {value === 'stat' && (
        <DataStat
          startDate={startDate}
          endDate={endDate}
          pageOffset={pageOffset}
        />
      )}
      {value === 'reject' && (
        <RejectedDataListComp
          startDate={startDate}
          endDate={endDate}
          pageOffset={pageOffset}
          specieValue={specieValue}
        />
      )}
      {value === 'list' && (
      <>
      <Box sx={{ marginTop: '30px' }}>
        <Box sx={{ display: 'flex', gap: 2, marginBottom: '20px' }}>
          <Button
            variant="contained"
            onClick={handleLoadData}
            disabled={loading}
            sx={{ backgroundColor: navy, '&:hover': { backgroundColor: '#0a2a4a' } }}
          >
            {loading ? <CircularProgress size={20} color="inherit" /> : '데이터 불러오기'}
          </Button>

          <Button variant="outlined" onClick={handleFilter} sx={{ borderColor: navy, color: navy }}>필터</Button>
          <Button variant="outlined" onClick={initializeData} sx={{ borderColor: navy, color: navy }}>데이터 초기화</Button>
        </Box>

        <PredictionTableTmp
          data={data}
          onSelectionChange={handleSelectionChange}
          onRowClick={handleRowClick}
        />

        <Typography sx={{ marginTop: '10px', color: navy }}>
          총 {data.length}개의 데이터
        </Typography>
        <FilterModal
          open={filterModalOpen}
          onClose={() => setFilterModalOpen(false)}
          onApply={handleApplyFilters}
          filters={filters}
          setFilters={setFilters}
        />
        </Box>
        <Box sx={{ display: 'flex', gap: 2, marginBottom: '20px' }}>
        <Button
          variant="contained"
          onClick={goLearningPage}
          disabled={selectedRows.length === 0}
          sx={{ backgroundColor: navy, '&:hover': { backgroundColor: '#0a2a4a' } }}
        >
          학습하기
        </Button>
        <Button
          variant="contained"
          onClick={goPredictPage}
          disabled={selectedRows.length === 0}
          sx={{ backgroundColor: navy, '&:hover': { backgroundColor: '#0a2a4a' } }}
        >
          예측하기
        </Button>
        </Box>
      </>)}
    </div>
  );
};

export default OldDashboard;
