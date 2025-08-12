// src/routes/Learning.js
import { useState, useEffect } from 'react';
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
import { fetchFilteredData } from '../API/fetchFileteredData';
import { fetchPrediction } from '../API/predictData';

// ===== Mock train (keep until backend ready) =====
const USE_MOCK_TRAIN = true;
const makeMockTrainResult = () => {
  const pad = (n) => (n < 10 ? `0${n}` : `${n}`);
  const now = new Date();
  const dateStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
  const minutes = Math.floor(10 + Math.random() * 30); // 10~40
  const auc = (0.78 + Math.random() * 0.1).toFixed(4);
  const r2 = (0.55 + Math.random() * 0.2).toFixed(2);
  const recall = (0.7 + Math.random() * 0.15).toFixed(2);
  const loss = (0.85 + Math.random() * 0.1).toFixed(4);
  // [생성날짜, 학습시간, AUC, R2, Recall, Loss]
  return [dateStr, `${minutes}min`, auc, r2, recall, loss];
};
// ================================================

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

  // 선택 데이터 예측
  const handlePredict = async () => {
    if (selectedRows.length === 0) {
      setSnackbar({ open: true, severity: 'warning', message: '예측할 데이터를 선택해주세요.' });
      return;
    }
    setLoading(true);
    try {
      const result = await fetchPrediction(selectedRows);
      // result가 배열 혹은 { [id]: prediction } 둘 다 지원
      const idToPred = Array.isArray(result)
        ? result.reduce((acc, r) => {
            if (r?.id && r?.prediction) acc[r.id] = r.prediction;
            return acc;
          }, {})
        : result;

      const newData = data.map((row) =>
        idToPred[row.id] ? { ...row, prediction: idToPred[row.id] } : row
      );
      setData(newData);
      setSnackbar({ open: true, severity: 'success', message: '예측 성공!' });
    } catch (err) {
      console.error('예측 실패:', err);
      setSnackbar({ open: true, severity: 'error', message: '예측 실패! 서버 상태를 확인해주세요.' });
    } finally {
      setLoading(false);
    }
  };

  // 필터 열기/적용
  const handleFilter = () => setFilterModalOpen(true);
  const handleApplyFilters = (applied) => {
    setFilters(applied);
    handleLoadData();
  };

  // 데이터 초기화
  const initializeData = () => setData([]);

  // 학습
  const handleTrain = async (trainDataSet) => {
    if (!trainDataSet || trainDataSet.length === 0) {
      setSnackbar({ open: true, severity: 'warning', message: '학습할 데이터가 없습니다.' });
      return;
    }
    setIsTraining(true);
    try {
      if (USE_MOCK_TRAIN) {
        const mockRow = makeMockTrainResult();
        setResults(mockRow);
        setSnackbar({ open: true, severity: 'success', message: '모델 학습이 완료되었습니다. (MOCK)' });
      } else {
        const response = await trainSpectralModel(trainDataSet);
        setResults(response); // response가 [..] 한 행 형태라고 가정
        setSnackbar({ open: true, severity: 'success', message: '모델 학습이 완료되었습니다.' });
      }
    } catch (error) {
      console.error('학습 실패:', error);
      setSnackbar({ open: true, severity: 'error', message: '모델 학습 중 오류가 발생했습니다.' });
      setIsTraining(false);
    }
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
  const getModelResults = () => ['생성 날짜', 'Train_Time', 'Test_AUC', 'R2_score', 'Recall', 'Loss'];

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
        <PredictionTable data={data} onSelectionChange={handleSelectionChange} onRowClick={handleRowClick} />

        <Typography sx={{ marginTop: '10px', color: navy }}>총 {data.length}개의 데이터</Typography>

        {/* 예측/학습/배포 */}
        <Box sx={{ display: 'flex', gap: 2, marginTop: '20px', marginBottom: '20px' }}>
          <Button
            variant="contained"
            onClick={() => handleTrain(data)}
            disabled={selectedRows.length === 0}
            sx={{ backgroundColor: '#28a745', '&:hover': { backgroundColor: '#218838' }, '&:disabled': { backgroundColor: '#6c757d' } }}
          >
            학습하기
          </Button>
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
