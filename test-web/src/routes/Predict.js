import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Box,
  Button,
  CircularProgress,
  Typography,
  Chip,
} from '@mui/material';
// components
import FilterModal from '../components/FilterModal';
import PredictionTable from '../components/PredictionTable';
import PredictionDetailPanel from '../components/PredictionDetailPanel';
import { Snackbar, Alert } from '@mui/material';
import { fetchPrediction } from '../API/predictData';
import ExportSelectedToExcel from '../components/ExportSelectedToExcel';

// 데이터 캐싱을 위한 import
import useFileList from '../Utils/useFileList';
import { useQueryClient } from '@tanstack/react-query';
import { usePrediction } from '../context/PredictionContext';

const navy = '#0F3659';

const Predict = () => {
  const location = useLocation();
  const queryClient = useQueryClient();

  // PredictionContext에서 필요한 함수들과 변수들을 가져옴
  const {
    isPredicting,
    startPrediction,
    updateProgress,
    completePrediction,
    closeProgressModal,
    closeResultModal,
  } = usePrediction();

  const [selectedRows, setSelectedRows] = useState([]);
  const [filterModalOpen, setFilterModalOpen] = useState(false);
  const [openPanel, setOpenPanel] = useState(false);
  const [detailData, setDetailData] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    severity: 'info',
    message: '',
  });
  const [filters, setFilters] = useState([
    { name: '날짜', type: 'date', options: [], value: { start: null, end: null } },
    { name: '품종', type: 'select', options: ['전체', '소', '돼지', '닭'], value: '전체' },
  ]);
  const [isLoaded, setIsLoaded] = useState(false); // query on/off

  const { data = [], isFetching, refetch } = useFileList(filters, { enabled: isLoaded });

  // Dashboard에서 넘어온 데이터로 초기화 + 새로고침 대비 sessionStorage 사용
  useEffect(() => {
    if (location.state?.selectedRows) {
      setSelectedRows(location.state.selectedRows);
    }
  }, [location.state]);

  // 데이터 불러오기 함수
  const handleLoadData = async () => {
    try {
      setIsLoaded(true);
      setTimeout(() => {
        refetch();
      }, 100);

      // 성공 여부 알림
      setSnackbar({
        open: true,
        severity: 'success',
        message: '데이터를 불러오는 중입니다...',
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

  // Rowclick 여부 다루기
  const handleRowClick = (row) => {
    if (!row.prediction) return;
    setDetailData({
      id: row.id,
      prediction: row.prediction,
      sensory: row.sensory,
    });
    setOpenPanel(true);
  };

  // 선택된 데이터 predict하기
  const handlePredict = async () => {
    if (selectedRows.length === 0) {
      setSnackbar({
        open: true,
        severity: 'warning',
        message: '예측할 데이터를 선택해주세요.'
      });
      return;
    }

    // 전역 예측 시작
    startPrediction();

    try {
      // 진행 상황 업데이트 콜백 함수
      const onProgressUpdate = (progress, totalCount, completedCount) => {
        console.log(`진행 상황 업데이트 콜백 호출:`, {
          progressLength: progress.length,
          totalCount,
          completedCount,
          progress: progress.map(p => ({ id: p.id, status: p.status, message: p.message }))
        });
        updateProgress(progress, totalCount, completedCount);
      };

      // 예측 시작
      const result = await fetchPrediction(selectedRows, data, onProgressUpdate);

      // 전역 예측 완료
      completePrediction(result.results || [], result.progress || []);

      // 성공 알림
      setSnackbar({
        open: true,
        severity: 'success',
        message: '예측이 완료되었습니다!'
      });

    } catch (err) {
      console.error('예측 실패:', err);
      setSnackbar({
        open: true,
        severity: 'error',
        message: '예측 실패! 서버 상태를 확인해주세요.',
      });

      // 진행 상황 모달 닫기
      closeProgressModal();
    }
  };

  // 필터 함수
  const handleFilter = () => {
    setFilterModalOpen(true);
  };

  const initializeData = () => {
    queryClient.removeQueries({ queryKey: ['fileList'] });
    setIsLoaded(false);
    setSelectedRows([]);
    setOpenPanel(false);
    setDetailData(null);

    // 예측 관련 상태 초기화
    closeProgressModal();
    closeResultModal();
  };

  // 필터 제거 함수
  const handleRemoveFilter = (filterName) => {
    const updatedFilters = filters.map((filter) => {
      if (filter.name === filterName) {
        if (filter.type === 'date') {
          return { ...filter, value: { start: null, end: null } };
        } else {
          return { ...filter, value: null };
        }
      }
      return filter;
    });

    setFilters(updatedFilters);
    handleLoadData(); // 필터 제거 후 데이터 다시 로드
  };

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
        if (categoryIds.some(id => id >= 0 && id <= 99)) specieValue = '소';
        else if (categoryIds.some(id => id >= 100 && id <= 199)) specieValue = '돼지';
        else if (categoryIds.some(id => id >= 200 && id <= 299)) specieValue = '닭';

        setFilters(prev => prev.map(f =>
          f.name === '품종'
            ? { ...f, value: specieValue }
            : f
        ));
      }
    }

    // 필터 적용 후 데이터 다시 로드
    setIsLoaded(true);
    setTimeout(() => {
      refetch();
    }, 100);
  };

  return (
    <div
      style={{
        overflow: 'auto',
        width: '100%',
        marginTop: '20px',
        height: '100%',
        paddingLeft: '30px',
        paddingRight: '20px',
      }}
    >
      <Box
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          minWidth: '634px',
        }}
      >
        <span style={{ color: `${navy}`, fontSize: '30px', fontWeight: '600' }}>
          AI Prediction
        </span>
      </Box>

      <Box sx={{ marginTop: '30px' }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
            marginBottom: '20px',
          }}
        >
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              onClick={handleLoadData}
              disabled={isFetching}
              sx={{
                backgroundColor: navy,
                '&:hover': { backgroundColor: '#0a2a4a' },
              }}
            >
              {isFetching ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                '데이터 불러오기'
              )}
            </Button>

            <Button
              variant="outlined"
              onClick={handleFilter}
              sx={{ borderColor: navy, color: navy }}
            >
              필터
            </Button>
            <Button
              variant="outlined"
              onClick={initializeData}
              sx={{ borderColor: navy, color: navy }}
            >
              데이터 초기화
            </Button>
          </Box>

          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              gap: 1,
              marginLeft: '2px',
            }}
          >
            <Typography variant="subtitle2" sx={{ color: '#444' }}>
              적용된 필터:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {filters.map((filter) => {
                // 날짜 필터 처리
                if (
                  filter.name === '날짜' &&
                  filter.value &&
                  (filter.value.start || filter.value.end)
                ) {
                  return (
                    <Chip
                      key={filter.name}
                      label={
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography
                            variant="body2"
                            sx={{ fontWeight: 'bold', marginRight: '4px' }}
                          >
                            {filter.name}:
                          </Typography>
                          <Typography variant="body2">
                            {filter.value.start
                              ? (typeof filter.value.start === 'string' ? filter.value.start : filter.value.start.format('YYYY-MM-DD'))
                              : '처음'}{' '}
                            ~{' '}
                            {filter.value.end
                              ? (typeof filter.value.end === 'string' ? filter.value.end : filter.value.end.format('YYYY-MM-DD'))
                              : '현재'}
                          </Typography>
                        </Box>
                      }
                      onDelete={() => handleRemoveFilter(filter.name)}
                      sx={{
                        backgroundColor: '#e3f2fd',
                        borderRadius: '16px',
                        padding: '4px',
                      }}
                      variant="outlined"
                    />
                  );
                }
                // 선택 필터 처리
                else if (filter.type === 'select' && filter.value) {
                  const isSpecieFilter = filter.name === '품종';
                  return (
                    <Chip
                      key={filter.name}
                      label={
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography
                            variant="body2"
                            sx={{ fontWeight: 'bold', marginRight: '4px' }}
                          >
                            {filter.name}:
                          </Typography>
                          <Typography variant="body2">
                            {filter.value}
                            {isSpecieFilter && (
                              <span
                                style={{
                                  fontSize: '0.8rem',
                                  marginLeft: '4px',
                                  color: '#555',
                                }}
                              >
                                (
                                {filter.value === '소'
                                  ? '소고기'
                                  : filter.value === '돼지'
                                    ? '돼지고기'
                                    : filter.value === '닭'
                                      ? '닭고기'
                                      : '전체'}
                                )
                              </span>
                            )}
                          </Typography>
                        </Box>
                      }
                      onDelete={() => handleRemoveFilter(filter.name)}
                      sx={{
                        backgroundColor: isSpecieFilter
                          ? filter.value === '소'
                            ? '#e8f5e9'
                            : filter.value === '돼지'
                              ? '#e0f7fa'
                              : filter.value === '닭'
                                ? '#fff3e0'
                                : '#e3f2fd'
                          : '#e3f2fd',
                        borderRadius: '16px',
                        padding: '4px',
                      }}
                      variant="outlined"
                    />
                  );
                }
                return null;
              })}
              {!filters.some(
                (f) =>
                  (f.name === '날짜' &&
                    f.value &&
                    (f.value.start || f.value.end)) ||
                  (f.type === 'select' && f.value)
              ) && (
                  <Typography variant="body2" sx={{ color: '#666' }}>
                    필터 버튼을 클릭하여 품종(소/돼지/닭) 및 기타 필터 조건을
                    설정할 수 있습니다.
                  </Typography>
                )}
            </Box>
          </Box>
        </Box>

        <PredictionTable
          data={data}
          onSelectionChange={handleSelectionChange}
          onRowClick={handleRowClick}
          selectedRows={selectedRows}
        />

        <Typography sx={{ marginTop: '10px', color: navy }}>
          총 {data.length}개의 데이터
        </Typography>

        <Box
          sx={{
            display: 'flex',
            gap: 2,
            marginTop: '20px',
            marginBottom: '20px',
          }}
        >
          <Button
            variant="contained"
            disabled={selectedRows.length === 0 || isPredicting}
            onClick={() => handlePredict()}
            sx={{
              backgroundColor: navy,
              '&:hover': { backgroundColor: '#0a2a4a' },
            }}
          >
            {isPredicting ? <CircularProgress size={20} color="inherit" /> : '예측하기'}
          </Button>

          <Button
            variant="outlined"
            disabled={isPredicting || selectedRows.length === 0}
            onClick={() => ExportSelectedToExcel(selectedRows, data)}
            sx={{ borderColor: navy, color: navy }}
          >
            EXCEL로 다운로드
          </Button>
        </Box>

        <PredictionDetailPanel
          open={openPanel}
          onClose={() => setOpenPanel(false)}
          predictionData={detailData}
          labels={[
            '색상(Color)',
            '향(Aroma)',
            '조직감(Texture)',
            '즙성(Juiciness)',
            '풍미(Flavor)',
            '전체 기호도',
          ]}
          showTableComparison={true}
        />

        <Snackbar
          open={snackbar.open}
          autoHideDuration={4000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
        </Snackbar>

        <FilterModal
          open={filterModalOpen}
          onClose={() => setFilterModalOpen(false)}
          onApply={handleApplyFilters}
          filters={filters || []}
          setFilters={setFilters}
        />

        {/* 전역 Context에서 관리되는 모달들이므로 여기서는 제거 */}
        {/* PredictionProgressModal과 PredictionResultModal은 GlobalPredictionModals에서 관리됨 */}
      </Box>
    </div>
  );
};

export default Predict;
