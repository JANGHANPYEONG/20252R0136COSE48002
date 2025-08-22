// src/routes/Learning.js
import { useState, useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { Box, Button, CircularProgress, Typography, Snackbar, Alert } from '@mui/material';

// components
import DataList from '../components/DataList';
import FilterModal from '../components/FilterModal';
import PredictionTable from '../components/PredictionTable';
import PredictionDetailPanel from '../components/PredictionDetailPanel';

// APIs
import trainSpectralModel from '../API/train/trainSpectralModel';
import deploySpectralModel from '../API/train/deploySpectralModel';
import { trainHSIModel, getHSITrainingStatus } from '../API/train/trainHSIModel';
import { fetchFilteredData } from '../API/fetchFileteredData';
import { fetchPrediction } from '../API/predictData';


const navy = '#0F3659';

const Learning = () => {
  const [value] = useState('spectral'); // 현재 탭(분광)
  const [data, setData] = useState([]);
  const [groupedData, setGroupedData] = useState([]);
  const [selectedRows, setSelectedRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterModalOpen, setFilterModalOpen] = useState(false);

  const [filters, setFilters] = useState([
    { name: '날짜', type: 'date', options: [], value: { start: null, end: null } },
  ]);

  // from Dashboard.js
  const location = useLocation();
  // 학습 결과
  const [results, setResults] = useState([]);        // 한 행([...]) 단위
  const [history, setHistory] = useState([]);        // 과거 결과들(행 배열)
  const [isTraining, setIsTraining] = useState(true);
  const [currentTrainId, setCurrentTrainId] = useState(null); // 현재 HSI 학습 ID
  const statusIntervalRef = useRef(null); // 상태 확인 인터벌을 저장할 ref

  // 상세 패널
  const [openPanel, setOpenPanel] = useState(false);
  const [detailData, setDetailData] = useState(null);

  const [snackbar, setSnackbar] = useState({ open: false, severity: 'info', message: '완료' });

  useEffect(() => {
    const saved = JSON.parse(localStorage.getItem('cachedResults') || '[]');
    setHistory(Array.isArray(saved) ? saved : []);
    if (Array.isArray(saved) && saved.length > 0) setIsTraining(false);
  }, []);


  useEffect(() => {
    if (location.state?.data) {
      setData(location.state.data);
    }
    if (location.state?.selectedRows) {
      setSelectedRows(location.state.selectedRows);
    }
  }, [location.state]);

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      // ref를 통해 실제 인터벌 ID에 접근하여 정리
      if (statusIntervalRef.current) {
        clearInterval(statusIntervalRef.current);
        statusIntervalRef.current = null;
      }
    };
  }, []);
  // 데이터 불러오기
  const handleLoadData = async () => {
    setLoading(true);
    try {
      const result = await fetchFilteredData(filters, value);
      setData(result);

      // 업로드 배치 단위 그룹핑(미사용이면 제거해도 무방)
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

      setSnackbar({
        open: true,
        severity: 'success',
        message: `데이터 ${result.length}개를 성공적으로 불러왔습니다.`,
      });
    } catch (err) {
      console.error('데이터 불러오기 실패:', err);
      setSnackbar({ open: true, severity: 'error', message: '데이터 불러오기 실패! 서버를 확인해주세요.' });
    } finally {
      setLoading(false);
    }
  };

  // 선택 변경
  const handleSelectionChange = (newSelection) => setSelectedRows(newSelection);

  // 행 클릭 → 상세 패널
  const handleRowClick = (row) => {
    if (!row.prediction) return;
    setDetailData({ id: row.id, prediction: row.prediction, sensory: row.sensory });
    setOpenPanel(true);
  };


  // 필터 열기/적용
  const handleFilter = () => setFilterModalOpen(true);
  const handleApplyFilters = (applied) => {
    setFilters(applied);
    handleLoadData();
  };

  // 데이터 초기화
  const initializeData = () => setData([]);

  // HSI 학습
  const handleHSITrain = async () => {
    // 선택된 육류 데이터의 ID 리스트 추출
    const idList = selectedRows.map(row => row.id);
    
    setIsTraining(true);
    try {
      const response = await trainHSIModel(idList);
      
      // 응답에서 필요한 정보 추출
      const { message, train_id, process_pid, created_at } = response;
      
      // 현재 학습 ID 저장
      setCurrentTrainId(train_id);
      
      // 학습 결과를 표시할 수 있도록 결과 저장
      const trainResult = [
        created_at.split('T')[0], // 날짜만 추출
        train_id.substring(0, 20), // train_id 일부만 표시
        process_pid.toString(),
        'HSI Training Started'
      ];
      
      setResults(trainResult);
      setSnackbar({ 
        open: true, 
        severity: 'success', 
        message: `HSI 학습이 시작되었습니다. (${idList.length}개 이미지)` 
      });
      
      console.log('HSI Training started:', response);
      
      // 학습 상태 주기적 확인 시작
      startStatusCheck(train_id);
    } catch (error) {
      console.error('HSI 학습 실패:', error);
      setSnackbar({ 
        open: true, 
        severity: 'error', 
        message: 'HSI 학습 시작 중 오류가 발생했습니다.' 
      });
      setIsTraining(false);
    }
  };

  // HSI 학습 상태 주기적 확인
  const startStatusCheck = async (trainId) => {
    // 기존 인터벌이 있다면 정리
    if (statusIntervalRef.current) {
      clearInterval(statusIntervalRef.current);
      statusIntervalRef.current = null;
    }
    
    const checkStatus = async () => {
      try {
        const statusResponse = await getHSITrainingStatus(trainId);
        const { status } = statusResponse;
        
        // 상태에 따라 결과 업데이트
        if (status === 'completed' || status === 'failed') {
          setIsTraining(false);
          
          // 결과 테이블 업데이트
          setResults(prev => {
            if (prev.length >= 4) {
              const newResults = [...prev];
              newResults[3] = status === 'completed' ? 'HSI Training Completed' : 'HSI Training Failed';
              return newResults;
            }
            return prev;
          });
          
          if (status === 'completed') {
            setSnackbar({ 
              open: true, 
              severity: 'success', 
              message: 'HSI 학습이 완료되었습니다!' 
            });
          } else {
            setSnackbar({ 
              open: true, 
              severity: 'error', 
              message: 'HSI 학습이 실패했습니다.' 
            });
          }
          
          // 상태 확인 중단
          if (statusIntervalRef.current) {
            clearInterval(statusIntervalRef.current);
            statusIntervalRef.current = null;
          }
        }
      } catch (error) {
        console.error('상태 확인 실패:', error);
      }
    };
    
    // 즉시 한 번 확인
    await checkStatus();
    
    // 10초마다 상태 확인하고 ref에 저장
    statusIntervalRef.current = setInterval(checkStatus, 10000);
  };



  // 배포
  const handleDeploy = () => {
    const newHistory = results.length ? [...history, results] : [...history];
    localStorage.setItem('cachedResults', JSON.stringify(newHistory));
    deploySpectralModel();
    setHistory(newHistory);
    setIsTraining(false);
  };

  // 학습 결과 테이블 컬럼
  const getModelResults = () => ['학습 날짜', 'Train ID', 'Process ID', 'message'];

  const displayResults = [...history, ...(results.length ? [results] : [])];

  return (
    <div style={{ overflow: 'auto', width: '100%', marginTop: '100px', height: '100%', paddingLeft: '30px', paddingRight: '20px' }}>
      {/* 페이지 제목 */}
      <Box style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', minWidth: '634px' }}>
        <span style={{ color: navy, fontSize: '30px', fontWeight: 600 }}>AI Training</span>
      </Box>

      <Box sx={{ marginTop: '30px' }}>
        {/* 버튼 영역 */}
        <Box sx={{ display: 'flex', gap: 2, marginBottom: '20px' }}>
          <Button
            variant="contained"
            onClick={handleLoadData}
            disabled={loading}
            sx={{ backgroundColor: navy, '&:hover': { backgroundColor: '#0a2a4a' } }}
          >
            {loading ? <CircularProgress size={20} color="inherit" /> : '데이터 불러오기'}
          </Button>
          <Button variant="outlined" onClick={handleFilter} sx={{ borderColor: navy, color: navy }}>
            필터
          </Button>
          <Button variant="outlined" onClick={initializeData} sx={{ borderColor: navy, color: navy }}>
            데이터 초기화
          </Button>
        </Box>

        {/* 데이터 테이블 + 선택/상세 */}
        <PredictionTable 
          data={data} 
          onSelectionChange={handleSelectionChange} 
          onRowClick={handleRowClick}
          selectedRows={selectedRows}
        />

        <Typography sx={{ marginTop: '10px', color: navy }}>총 {data.length}개의 데이터</Typography>

        {/* 예측/학습/배포 */}
        <Box sx={{ display: 'flex', gap: 2, marginTop: '20px', marginBottom: '20px' }}>
          <Button
            variant="contained"
            onClick={handleHSITrain}
            disabled={selectedRows.length === 1}
            sx={{ backgroundColor: '#28a745', '&:hover': { backgroundColor: '#218838' }, '&:disabled': { backgroundColor: '#6c757d' } }}
          >
            HSI 학습하기
          </Button>
          {currentTrainId && (
            <Button
              variant="outlined"
              onClick={() => {
                // 기존 인터벌 정리 후 새로 시작
                if (statusIntervalRef.current) {
                  clearInterval(statusIntervalRef.current);
                  statusIntervalRef.current = null;
                }
                startStatusCheck(currentTrainId);
              }}
              sx={{ borderColor: '#007bff', color: '#007bff' }}
            >
              상태 확인
            </Button>
          )}
        </Box>

        {/* 학습 결과 비교 표 */}
        {displayResults.length > 0 && (
          <DataList columns={getModelResults()} data={displayResults} disabled={!isTraining} title="모델 학습 결과 비교" />
        )}

        {/* 상세 패널 */}
        <PredictionDetailPanel
          open={openPanel}
          onClose={() => setOpenPanel(false)}
          predictionData={detailData}
          labels={['색상(Color)', '향(Aroma)', '조직감(Texture)', '즙성(Juiciness)', '풍미(Flavor)', '전체 기호도']}
          showTableComparison
        />
        <Box sx={{ display: 'flex', gap: 2, marginTop: '20px', marginBottom: '20px' }}></Box>
        <Button
          variant="contained"
          onClick={handleDeploy}
          disabled={!results.length}
          sx={{ backgroundColor: '#28a745', '&:hover': { backgroundColor: '#218838' }, '&:disabled': { backgroundColor: '#6c757d' } }}
        >
          배포하기
        </Button>
        {/* 스낵바 */}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={4000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
        </Snackbar>

        {/* 필터 모달 */}
        <FilterModal
          open={filterModalOpen}
          onClose={() => setFilterModalOpen(false)}
          onApply={handleApplyFilters}
          filters={filters}
          setFilters={setFilters}
        />
      </Box>
    </div>
  );
};

export default Learning;
