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

// 캐싱용 패치
import useFileList from '../Utils/useFileList';
import { useQueryClient } from '@tanstack/react-query'
import { Filter6Sharp } from '@mui/icons-material';

const navy = '#0F3659';

const Dashboard = () => {
  const [value, setValue] = useState('list');
  const [specieValue, setSpecieValue] = useState('전체');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [pageOffset, setPageOffset] = useState(1);
  const [isLoading, setIsLoading] = useState(true);

  const [searchedData, setSearchedData] = useState(null);
  // temp for mocking
  const [groupedData, setGroupedData] = useState([]);
  const [selectedRows, setSelectedRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterModalOpen, setFilterModalOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, severity: 'info', message: '완료' });


  const [filters, setFilters] = useState([
    { name: '날짜', type: 'date', options: [], value: { start: null, end: null } },
    { name: '품종', type: 'select', options: ['전체', '소', '돼지', '닭'], value: '전체' },
    { name: 'page', type: 'select', options: [1, 2, 3, 4, 5], value: 1 },
    { name: 'pageSize', type: 'select', options: [10, 25, 50, 100], value: 50 },
  ]);
  const navigate = useNavigate();
  const [openPanel, setOpenPanel] = useState(false);
  const [detailData, setDetailData] = useState(null);
  //////////////////////////////////////////////////
  // data를 useState로 저장 -> usequeryClient 로 저장
  const [isLoaded, setisLoaded] = useState(false); // query on/off
  const queryClient = useQueryClient();
  const { data = [], isFetching, refetch } = useFileList(filters, { enabled: isLoaded });


  // 쿼리스트링 추출
  const location = useLocation();
  const { querypageOffset, queryStartDate, queryEndDate, queryDuration } =
    useMemo(() => {
      const searchParams = new URLSearchParams(location.search);
      return {
        querypageOffset: searchParams.get('pageOffset'),
        queryStartDate: searchParams.get('start') || '',
        queryEndDate: searchParams.get('end') || '',
        queryDuration: searchParams.get('duration') || '',
      };
    }, [location.search]);

  useEffect(() => {
    setPageOffset(querypageOffset);
  }, [querypageOffset]);

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
      // 기본값 설정 (7일 전부터 현재까지)
      start = new Date(now);
      start.setDate(now.getDate() - 7);
    }

    const formattedStartDate = new Date(start.getTime() + TIME_ZONE)
      .toISOString()
      .slice(0, -5);
    const formattedEndDate = new Date(end.getTime() + TIME_ZONE)
      .toISOString()
      .slice(0, -5);

    setStartDate(formattedStartDate);
    setEndDate(formattedEndDate);

    // 날짜 필터 업데이트
    setFilters(prev => prev.map(f =>
      f.name === '날짜'
        ? { ...f, value: { start: formattedStartDate.split('T')[0], end: formattedEndDate.split('T')[0] } }
        : f
    ));

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
    } catch { }

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
    } catch { }

    navigate('/predict', { state: { data: payload, selectedRows: selectedRows, from: 'dashboard' } });
  };
  // 데이터 불러오기 함수
  const handleLoadData = async () => {
    try {
      const { data: fresh } = await refetch();
      const list = fresh ?? [];
      const groupMap = {};
      list.forEach((item) => {
        // butcheryYmd를 기준으로 그룹화
        const batchId = item.butcheryYmd ? item.butcheryYmd.split('T')[0] : 'Unknown';
        if (!groupMap[batchId]) groupMap[batchId] = [];
        groupMap[batchId].push(item);
      });
      const grouped = Object.entries(groupMap).map(([batchId, rows]) => ({
        batchId,
        timestamp: batchId,
        rows,
      }));

      setGroupedData(grouped);
      // 성공 여부 알림
      setSnackbar({
        open: true,
        severity: 'success',
        message: `데이터 ${list.length}개를 성공적으로 불러왔습니다.`,
      });
    } catch (err) {
      console.error('데이터 불러오기 실패:', err);
      setSnackbar({
        open: true,
        severity: 'error',
        message: '데이터 불러오기 실패! 서버를 확인해주세요.',
      });
    }
  };

  // 선택 변경 핸들러
  const handleSelectionChange = (newSelection) => {
    setSelectedRows(newSelection);
  };



  // 필터 함수
  const handleFilter = () => {
    setFilterModalOpen(true);
  };

  // 데이터 초기화 함수
  const initializeData = async () => {
    // 1) 진행 중인 요청 취소 (안 하면 응답이 도착하며 다시 채워질 수 있음)
    await queryClient.cancelQueries({ queryKey: ['fileList'] });
    // 2) 현재 붙어있는 쿼리들의 데이터를 즉시 빈 배열로 설정 (UI 즉시 비우기)
    queryClient.setQueriesData({ queryKey: ['fileList'] }, () => []);
    // 3) 캐시 항목 자체 제거 (다른 변형 키들도 함께)
    queryClient.removeQueries({ queryKey: ['fileList'] });
    // query loading off
    setisLoaded(false);
    // 4) UI 상태 리셋
    setGroupedData([]);
    setSelectedRows([]);
    setOpenPanel(false);
    setDetailData(null);
    sessionStorage.removeItem('predict_data');

    // 5) 필터 초기화
    setFilters([
      { name: '날짜', type: 'date', options: [], value: { start: startDate.split('T')[0], end: endDate.split('T')[0] } },
      { name: '품종', type: 'select', options: ['전체', '소', '돼지', '닭'], value: '전체' },
      { name: 'page', type: 'select', options: [1, 2, 3, 4, 5], value: 1 },
      { name: 'pageSize', type: 'select', options: [10, 25, 50, 100], value: 50 },
    ]);
  }
  // 필터 적용 함수
  const handleApplyFilters = (appliedFilters) => {
    // appliedFilters는 백엔드용 필터 객체이므로, UI용 필터 상태는 유지
    console.log('적용된 필터:', appliedFilters);

    // 백엔드 필터를 UI 필터 상태에 반영
    if (appliedFilters.filters) {
      const { categoryIds, butcheryYmd_from, butcheryYmd_to } = appliedFilters.filters;

      // 날짜 필터 업데이트
      if (butcheryYmd_from || butcheryYmd_to) {
        setFilters(prev => prev.map(f =>
          f.name === '날짜'
            ? {
              ...f, value: {
                start: butcheryYmd_from ? butcheryYmd_from.split('T')[0] : null,
                end: butcheryYmd_to ? butcheryYmd_to.split('T')[0] : null
              }
            }
            : f
        ));
      }

      // 품종 필터 업데이트
      if (categoryIds && categoryIds.length > 0) {
        let specieValue = '전체';
        if (categoryIds.some(id => id >= 0 && id <= 9)) specieValue = '소';
        else if (categoryIds.some(id => id >= 10 && id <= 20)) specieValue = '돼지';
        else if (categoryIds.some(id => id >= 30 && id <= 40)) specieValue = '닭';

        setFilters(prev => prev.map(f =>
          f.name === '품종'
            ? { ...f, value: specieValue }
            : f
        ));
      }
    }

    // 필터 적용 후 데이터 다시 로드
    setisLoaded(true);
    setTimeout(() => {
      handleLoadData();
    }, 100);
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
                onClick={() => {
                  setisLoaded(true);
                  setTimeout(() => {
                    handleLoadData();
                  }, 100);
                }}
                disabled={isFetching}
                sx={{ backgroundColor: navy, '&:hover': { backgroundColor: '#0a2a4a' } }}
              >
                {isFetching ? <CircularProgress size={20} color="inherit" /> : '데이터 불러오기'}
              </Button>

              <Button variant="outlined" onClick={handleFilter} sx={{ borderColor: navy, color: navy }}>필터</Button>
              <Button variant="outlined" onClick={initializeData} sx={{ borderColor: navy, color: navy }}>데이터 초기화</Button>
            </Box>

            <PredictionTableTmp
              data={data}
              onSelectionChange={handleSelectionChange}
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
              startDate={startDate}
              endDate={endDate}
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

export default Dashboard;
