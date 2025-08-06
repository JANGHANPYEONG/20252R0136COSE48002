import { useState } from 'react';
import { Box, Button, CircularProgress, Typography } from '@mui/material';
// style
import style from './style/dashboardstyle';
// components
import DataList from '../components/DataList';
import FilterModal from '../components/FilterModal';
import { fetchFilteredData } from '../API/fetchFileteredData';
import { Snackbar, Alert } from '@mui/material';


const navy = '#0F3659';

const Learning = () => {
  const [value, setValue] = useState('photo');
  const [data, setData] = useState([]);
  const [models, setModels] = useState([]);
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
  const handleValueChange = (newValue) => {
    setValue(newValue);
  };

  // 데이터 불러오기 함수
  const handleLoadData = async () => {
    setLoading(true);
    // 실제 API 호출 로직이 여기에 들어갈 예정
    // 필터 선택 옵션 추가적인 구현 필요
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
    setLoading(false);
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

  // 학습하기 함수
  const handleTrain = () => {
    console.log('학습 시작');
  };

  // 탭별 컬럼 설정
  const getColumns = () => {
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

  // 탭별 모델 컬럼 설정
  const getModelColumns = () => {
    return ['모델명', '생성일', '정확도', '상태'];
  };

  return (
    // 불러오기 Snackbar 랜더링
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
          AI Training
        </span>
      </Box>

      {/**탭별 콘텐츠 */}
      <Box sx={{ marginTop: '30px' }}>
        {value === 'photo' && (
          <Box>
            {/* 버튼 영역 */}
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
              <Button
                variant="outlined"
                onClick={handleFilter}
                sx={{ borderColor: navy, color: navy }}
              >
                필터
              </Button>
            </Box>
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


            {/* 데이터 리스트 */}
            <DataList
              columns={getColumns()}
              data={data}
              title="분광 데이터 목록"
            />

            {/* 데이터 개수 */}
            <Typography sx={{ marginTop: '10px', color: navy }}>
              총 {data.length}개의 데이터
            </Typography>

            {/* 학습하기 버튼 */}
            <Box sx={{ marginTop: '20px', marginBottom: '20px' }}>
              <Button
                variant="contained"
                onClick={handleTrain}
                disabled={data.length === 0}
                sx={{
                  backgroundColor: '#28a745',
                  '&:hover': { backgroundColor: '#218838' },
                  '&:disabled': { backgroundColor: '#6c757d' },
                }}
              >
                학습하기
              </Button>
            </Box>

            {/* 모델 목록 */}
            <DataList
              columns={getModelColumns()}
              data={models}
              title="모델 목록"
            />
          </Box>
        )}

        {value === 'spectral' && (
          <Box>
            {/* 버튼 영역 */}
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
              columns={getColumns()}
              data={data}
              title="분광 데이터 목록"
            />

            {/* 데이터 개수 */}
            <Typography sx={{ marginTop: '10px', color: navy }}>
              총 {data.length}개의 데이터
            </Typography>

            {/* 학습하기 버튼 */}
            <Box sx={{ marginTop: '20px', marginBottom: '20px' }}>
              <Button
                variant="contained"
                onClick={handleTrain}
                disabled={data.length === 0}
                sx={{
                  backgroundColor: '#28a745',
                  '&:hover': { backgroundColor: '#218838' },
                  '&:disabled': { backgroundColor: '#6c757d' },
                }}
              >
                학습하기
              </Button>
            </Box>

            {/* 모델 목록 */}
            <DataList
              columns={getModelColumns()}
              data={models}
              title="모델 목록"
            />
          </Box>
        )}

        {value === 'cross' && (
          <Box>
            {/* 버튼 영역 */}
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
              columns={getColumns()}
              data={data}
              title="Cross 데이터 목록"
            />

            {/* 데이터 개수 */}
            <Typography sx={{ marginTop: '10px', color: navy }}>
              총 {data.length}개의 데이터
            </Typography>

            {/* 학습하기 버튼 */}
            <Box sx={{ marginTop: '20px', marginBottom: '20px' }}>
              <Button
                variant="contained"
                onClick={handleTrain}
                disabled={data.length === 0}
                sx={{
                  backgroundColor: '#28a745',
                  '&:hover': { backgroundColor: '#218838' },
                  '&:disabled': { backgroundColor: '#6c757d' },
                }}
              >
                학습하기
              </Button>
            </Box>

            {/* 모델 목록 */}
            <DataList
              columns={getModelColumns()}
              data={models}
              title="모델 목록"
            />
          </Box>
        )}
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

export default Learning;
