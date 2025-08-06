import { useState } from 'react';
import {
  Box,
  Button,
  CircularProgress,
  Typography,
  Paper,
} from '@mui/material';
// style
import style from './style/dashboardstyle';
// components
import DataList from '../components/DataList';
import FilterModal from '../components/FilterModal';
import { fetchFilteredData } from '../API/fetchFileteredData';
import { Snackbar, Alert } from '@mui/material';
const navy = '#0F3659';

const Predict = () => {
  const [value, setValue] = useState('spectral');
  //   const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterModalOpen, setFilterModalOpen] = useState(false);
  const [filters, setFilters] = useState([
    {
      name: '날짜',
      type: 'date',
      options: [],
      value: { start: null, end: null },
    },
  ]);
  const [ snackbar, setSnackbar] = useState({
    open: false,
    severity: 'info',
    message:'완료',
  });

  //   const handleValueChange = (newValue) => {
  //     setValue(newValue);
  //     setSelectedModel(null); // 탭 변경 시 선택된 모델 초기화
  //   };

  // 모델 불러오기 함수
  //   const handleLoadModels = () => {
  //     setLoading(true);
  //     // 실제 API 호출 로직이 여기에 들어갈 예정
  //     setTimeout(() => {
  //       setModels([
  //         {
  //           id: 1,
  //           name: '사진모델_v1.0',
  //           createdDate: '2024-01-01',
  //           accuracy: '95.2%',
  //           status: '완료',
  //         },
  //         {
  //           id: 2,
  //           name: '사진모델_v1.1',
  //           createdDate: '2024-01-15',
  //           accuracy: '96.1%',
  //           status: '완료',
  //         },
  //       ]);
  //       setLoading(false);
  //     }, 1000);
  //   };

  //   // 모델 선택 함수
  //   const handleModelSelect = (model) => {
  //     setSelectedModel(model);
  //     console.log('선택된 모델:', model);
  //   };

  // 데이터 불러오기 함수
  const handleLoadData = async () => {
    setLoading(true);
    // 실제 API 호출 로직이 여기에 들어갈 예정
    // 필터 옵현 추가해야함
    try {
      const result = await fetchFilteredData(filters, value);
      setData(result);
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

  // 필터 함수
  const handleFilter = () => {
    setFilterModalOpen(true);
  };

  // 필터 적용 함수
  const handleApplyFilters = (appliedFilters) => {
    setFilters(appliedFilters);
    console.log('적용된 필터:', appliedFilters);
    // 여기서 필터링된 데이터를 API로 요청
    handleLoadData(); // 필터 적용 후 데이터 다시 로드
  };

  // 예측하기 함수
  const handlePredict = () => {
    console.log('예측 시작');
  };

  // 탭별 모델 컬럼 설정
  //   const getModelColumns = () => {
  //     return ['모델명', '생성일', '정확도', '상태'];
  //   };

  // 탭별 데이터 컬럼 설정
  const getDataColumns = () => {
    switch (value) {
      case 'photo':
        return ['ID', '파일명', '회차', '날짜', '마블링', '수분도', '총점'];
      case 'spectral':
        return ['ID', '스펙트럼', '파장', '날짜'];
      case 'cross':
        return ['ID', '사진ID', '스펙트럼ID', '날짜'];
      default:
        return ['ID', '이름', '타입', '날짜'];
    }
  };

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
      {/**페이지 제목 */}
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

      {/**이동 탭 (사진 데이터 모델, 분광 데이터 모델, Cross 모델) */}
      {/* <Box sx={style.fixedTab}>
        <div style={{ display: 'flex' }}>
          <Button
            style={value === 'photo' ? style.tabBtnCilcked : style.tabBtn}
            value="photo"
            variant="outlined"
            onClick={(e) => {
              handleValueChange(e.target.value);
            }}
          >
            사진 데이터 모델
          </Button>
          <Button
            style={value === 'spectral' ? style.tabBtnCilcked : style.tabBtn}
            value="spectral"
            variant="outlined"
            onClick={(e) => {
              handleValueChange(e.target.value);
            }}
          >
            분광 데이터 모델
          </Button>
          <Button
            style={value === 'cross' ? style.tabBtnCilcked : style.tabBtn}
            value="cross"
            variant="outlined"
            onClick={(e) => {
              handleValueChange(e.target.value);
            }}
          >
            Cross 모델
          </Button>
        </div>
      </Box> */}

      {/**탭별 콘텐츠 */}
      {/* <Box sx={{ marginTop: '30px' }}>
        {value === 'photo' && (
          <Box> */}
      {/* 모델 불러오기 버튼 */}
      {/* <Box sx={{ display: 'flex', gap: 2, marginBottom: '20px' }}>
              <Button
                variant="contained"
                onClick={handleLoadModels}
                disabled={loading}
                sx={{
                  backgroundColor: navy,
                  '&:hover': { backgroundColor: '#0a2a4a' },
                }}
              >
                {loading ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  '모델 불러오기'
                )}
              </Button>
            </Box> */}

      {/* 모델 목록 */}
      {/* <DataList
              columns={getModelColumns()}
              data={models}
              title="사진 데이터 모델 목록"
              onRowClick={handleModelSelect}
            /> */}

      {/* 선택된 모델 정보 */}
      {/* {selectedModel && (
              <Paper
                sx={{
                  padding: '20px',
                  marginTop: '20px',
                  backgroundColor: '#f8f9fa',
                }}
              >
                <Typography
                  variant="h6"
                  sx={{ color: navy, marginBottom: '15px' }}
                >
                  선택된 모델 정보
                </Typography>
                <Box
                  sx={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gap: 2,
                  }}
                >
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      학습날짜
                    </Typography>
                    <Typography variant="body1">
                      {selectedModel.createdDate}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      모델파일명
                    </Typography>
                    <Typography variant="body1">
                      {selectedModel.name}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      비고
                    </Typography>
                    <Typography variant="body1">
                      {selectedModel.status}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            )}
          </Box>
        )} */}

      {/* {value === 'spectral' && (
          <Box> */}
      {/* 모델 불러오기 버튼 */}
      {/* <Box sx={{ display: 'flex', gap: 2, marginBottom: '20px' }}>
              <Button
                variant="contained"
                onClick={handleLoadModels}
                disabled={loading}
                sx={{
                  backgroundColor: navy,
                  '&:hover': { backgroundColor: '#0a2a4a' },
                }}
              >
                {loading ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  '모델 불러오기'
                )}
              </Button>
            </Box> */}

      {/* 모델 목록 */}
      {/* <DataList
              columns={getModelColumns()}
              data={models}
              title="분광 데이터 모델 목록"
              onRowClick={handleModelSelect}
            /> */}

      {/* 선택된 모델 정보 */}
      {/* {selectedModel && (
              <Paper
                sx={{
                  padding: '20px',
                  marginTop: '20px',
                  backgroundColor: '#f8f9fa',
                }}
              >
                <Typography
                  variant="h6"
                  sx={{ color: navy, marginBottom: '15px' }}
                >
                  선택된 모델 정보
                </Typography>
                <Box
                  sx={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gap: 2,
                  }}
                >
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      학습날짜
                    </Typography>
                    <Typography variant="body1">
                      {selectedModel.createdDate}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      모델파일명
                    </Typography>
                    <Typography variant="body1">
                      {selectedModel.name}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      비고
                    </Typography>
                    <Typography variant="body1">
                      {selectedModel.status}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            )}
          </Box>
        )} */}

      {/* {value === 'cross' && (
          <Box> */}
      {/* 모델 불러오기 버튼 */}
      {/* <Box sx={{ display: 'flex', gap: 2, marginBottom: '20px' }}>
              <Button
                variant="contained"
                onClick={handleLoadModels}
                disabled={loading}
                sx={{
                  backgroundColor: navy,
                  '&:hover': { backgroundColor: '#0a2a4a' },
                }}
              >
                {loading ? (
                  <CircularProgress size={20} color="inherit" />
                ) : (
                  '모델 불러오기'
                )}
              </Button>
            </Box> */}

      {/* 모델 목록 */}
      {/* <DataList
              columns={getModelColumns()}
              data={models}
              title="Cross 모델 목록"
              onRowClick={handleModelSelect}
            /> */}

      {/* 선택된 모델 정보 */}
      {/* {selectedModel && (
              <Paper
                sx={{
                  padding: '20px',
                  marginTop: '20px',
                  backgroundColor: '#f8f9fa',
                }}
              >
                <Typography
                  variant="h6"
                  sx={{ color: navy, marginBottom: '15px' }}
                >
                  선택된 모델 정보
                </Typography>
                <Box
                  sx={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gap: 2,
                  }}
                >
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      학습날짜
                    </Typography>
                    <Typography variant="body1">
                      {selectedModel.createdDate}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      모델파일명
                    </Typography>
                    <Typography variant="body1">
                      {selectedModel.name}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2" color="textSecondary">
                      비고
                    </Typography>
                    <Typography variant="body1">
                      {selectedModel.status}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            )}
          </Box>
        )}
      </Box> */}

      {/* 공통 영역 - 데이터 불러오기 및 예측 */}
      <Box sx={{ marginTop: '30px' }}>
        {/* 데이터 불러오기 버튼 */}
        <Box sx={{ display: 'flex', gap: 2, marginBottom: '20px' }}>
          <Button
            variant="contained"
            onClick={handleLoadData}
            disabled={loading}
            sx={{
              backgroundColor: navy,
              '&:hover': { backgroundColor: '#0a2a4a' },
            }}
          >
            {loading ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              '데이터 불러오기'
            )}
          </Button>
          <Snackbar
            open={snackbar.open}
            autoHideDuration={3000}
            onClose={() => setSnackbar({ ...snackbar, open: false })}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
          >
            <Alert
              onClose={() => setSnackbar({ ...snackbar, open: false })}
              severity={snackbar.severity}
              sx={{ width: '100%' }}
            >
              {snackbar.message}
            </Alert>
          </Snackbar>
          <Button
            variant="outlined"
            onClick={handleFilter}
            sx={{ borderColor: navy, color: navy }}
          >
            필터
          </Button>
        </Box>

        {/* 데이터 리스트 */}
        <DataList
          columns={getDataColumns()}
          data={data}
          title="예측 데이터 목록"
        />

        {/* 데이터 개수 */}
        <Typography sx={{ marginTop: '10px', color: navy }}>
          총 {data.length}개의 데이터
        </Typography>

        {/* 예측하기 버튼 */}
        <Box sx={{ marginTop: '20px', marginBottom: '20px' }}>
          <Button
            variant="contained"
            onClick={handlePredict}
            disabled={data.length === 0 || !selectedModel}
            sx={{
              backgroundColor: '#28a745',
              '&:hover': { backgroundColor: '#218838' },
              '&:disabled': { backgroundColor: '#6c757d' },
            }}
          >
            예측하기
          </Button>
        </Box>
      </Box>

      {/* 필터 모달 */}
      <FilterModal
        open={filterModalOpen}
        onClose={() => setFilterModalOpen(false)}
        onApply={handleApplyFilters}
        filters={filters}
        setFilters={setFilters}
      />
    </div>
  );
};

export default Predict;
