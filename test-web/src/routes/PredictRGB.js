import { useState, useEffect } from 'react';
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
import PredictionTable from '../components/PredictionTable';
import PredictionDetailPanel from '../components/PredictionDetailPanel';
import { fetchFilteredData } from '../API/fetchFileteredData';
import { Snackbar, Alert } from '@mui/material';
import { fetchPrediction } from '../API/predictData';
import ExportSelectedToExcel from '../components/ExportSelectedToExcel';
const navy = '#0F3659';

const Predict = () => {
  const [value, setValue] = useState('spectral');
  const [data, setData] = useState([]);
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

  // Dummy data for Predict page
  // useEffect(() => {
  //   const dummy = [
  //     {
  //       id: 'M001',
  //       timestamp: '2025-08-07T10:15:00',
  //       date: '2025-08-07',
  //       spectrum: '...',
  //       wavelength: '650nm',
  //       prediction: {
  //         '색상(Color)': 7.2,
  //         '향(Aroma)': 6.8,
  //         '조직감(Texture)': 6.9,
  //         '즙성(Juiciness)': 6.5,
  //         '풍미(Flavor)': 7.1,
  //         '전체 기호도': 7.0,
  //       },
  //       sensory: {
  //         '색상(Color)': 7.0,
  //         '향(Aroma)': 6.5,
  //         '조직감(Texture)': 7.0,
  //         '즙성(Juiciness)': 6.2,
  //         '풍미(Flavor)': 6.8,
  //         '전체 기호도': 6.9,
  //       },
  //     },
  //     {
  //       id: 'M002',
  //       timestamp: '2025-08-07T10:15:00',
  //       date: '2025-08-07',
  //       spectrum: '...',
  //       wavelength: '650nm',
  //       // 예측 없음
  //     },
  //     {
  //       id: 'M003',
  //       timestamp: '2025-08-07T11:20:00',
  //       date: '2025-08-07',
  //       spectrum: '...',
  //       wavelength: '660nm',
  //       prediction: {
  //         '색상(Color)': 8.1,
  //         '향(Aroma)': 7.4,
  //         '조직감(Texture)': 7.0,
  //         '즙성(Juiciness)': 6.8,
  //         '풍미(Flavor)': 7.5,
  //         '전체 기호도': 7.6,
  //       },
  //       sensory: {
  //         '색상(Color)': 8.0,
  //         '향(Aroma)': 7.0,
  //         '조직감(Texture)': 6.9,
  //         '즙성(Juiciness)': 6.5,
  //         '풍미(Flavor)': 7.2,
  //         '전체 기호도': 7.4,
  //       },
  //     },
  //   ];

  //   setData(dummy);
  // }, []);



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

    return (
    <div style={{ overflow: 'auto', width: '100%', marginTop: '100px', height: '100%', paddingLeft: '30px', paddingRight: '20px' }}>
      <Box style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', minWidth: '634px' }}>
        <span style={{ color: `${navy}`, fontSize: '30px', fontWeight: '600' }}>AI Prediction</span>
      {/* 오른쪽 끝에 RGB 추가*/}
      <span style={{ color: `${navy}`, fontSize: '30px', fontWeight: '600' }}>RGB</span>      
      </Box>


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

        <PredictionTable
          data={data}
          onSelectionChange={handleSelectionChange}
          onRowClick={handleRowClick}
        />

        <Typography sx={{ marginTop: '10px', color: navy }}>
          총 {data.length}개의 데이터
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, marginTop: '20px', marginBottom: '20px' }}>
          <Button
            variant="contained"
            disabled={selectedRows.length === 0}
            onClick={() => handlePredict()}
            sx={{ backgroundColor: navy, '&:hover': { backgroundColor: '#0a2a4a' } }}
          >
            예측하기
          </Button>

          <Button
            variant="outlined"
            disabled={selectedRows.length === 0}
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
            '전체 기호도'
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
          filters={filters}
          setFilters={setFilters}
        />
      </Box>  
    </div>
  );
};



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
export default Predict;
