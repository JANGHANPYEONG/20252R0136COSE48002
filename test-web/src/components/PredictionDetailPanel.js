import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Typography,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  Paper,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  Radar,
  Legend,
  PolarRadiusAxis,
} from 'recharts';

const PredictionDetailPanel = ({
  open,
  onClose,
  predictionData,
  labels = [],
  showTableComparison = false,
}) => {
  const [selectedChart, setSelectedChart] = useState('both');
  const [currentPage, setCurrentPage] = useState('prediction'); // 'prediction' | 'xai'

  if (!predictionData) return null;
  const { id, prediction, sensory } = predictionData;

  // Recharts용 데이터 변환 (label 기준 정렬)
  const chartData = labels.map((key) => ({
    항목: key,
    예측값: prediction?.[key] ?? null,
    관능평가: sensory?.[key] ?? null,
  }));

  const handleChartToggle = (chartType) => {
    setSelectedChart(chartType);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const renderXAIContent = () => {
    return (
      <Box>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', color: '#1976d2' }}>
          XAI 분석 결과
        </Typography>
        
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          CNN 모델의 예측 결과에 대한 설명 가능한 인공지능 분석
        </Typography>

        <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
            Heatmap 분석 결과
          </Typography>
          
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'center', 
            mt: 2,
            border: '2px solid #e0e0e0',
            borderRadius: '8px',
            padding: '16px',
            backgroundColor: '#fafafa'
          }}>
            <img 
              src="/XAI/image_heatmap/heatmap.png"
              alt="XAI Heatmap Analysis"
              style={{
                maxWidth: '100%',
                maxHeight: '400px',
                objectFit: 'contain'
              }}
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <Typography 
              variant="body2" 
              color="textSecondary" 
              sx={{ display: 'none', alignSelf: 'center' }}
            >
              Heatmap 이미지를 불러올 수 없습니다.
            </Typography>
          </Box>
          
          <Typography variant="body2" sx={{ mt: 2, color: '#666' }}>
            빨간색 영역: 모델이 예측에 중요하게 고려한 부위<br/>
            파란색 영역: 예측에 덜 중요한 부위
          </Typography>
        </Paper>

        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            분석 요약
          </Typography>
          <Paper elevation={1} sx={{ p: 2, backgroundColor: '#f8f9fa' }}>
            <Typography variant="body2">
              • 모델은 육류의 중앙 부분을 가장 중요하게 고려했습니다.<br/>
              • 지방층과 근육 조직의 경계면이 품질 예측에 영향을 미쳤습니다.<br/>
              • 전반적으로 일정한 패턴의 특징을 학습한 것으로 보입니다.
            </Typography>
          </Paper>
        </Box>
      </Box>
    );
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            {currentPage === 'prediction' ? '예측 상세 정보' : 'XAI 분석 결과'} - {id}
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            {/* 페이지 네비게이션 버튼 */}
            <IconButton 
              onClick={() => handlePageChange('prediction')}
              disabled={currentPage === 'prediction'}
              size="small"
              sx={{ 
                backgroundColor: currentPage === 'prediction' ? '#e3f2fd' : 'transparent',
                '&:hover': { backgroundColor: '#e3f2fd' }
              }}
            >
              <NavigateBeforeIcon />
            </IconButton>
            <Typography variant="body2" sx={{ minWidth: '60px', textAlign: 'center' }}>
              {currentPage === 'prediction' ? '1 / 2' : '2 / 2'}
            </Typography>
            <IconButton 
              onClick={() => handlePageChange('xai')}
              disabled={currentPage === 'xai'}
              size="small"
              sx={{ 
                backgroundColor: currentPage === 'xai' ? '#e3f2fd' : 'transparent',
                '&:hover': { backgroundColor: '#e3f2fd' }
              }}
            >
              <NavigateNextIcon />
            </IconButton>
            <IconButton onClick={onClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent>
        {currentPage === 'prediction' ? (
          <>
            <Typography
              variant="subtitle1"
              gutterBottom
              sx={{ fontWeight: 'bold' }}
            >
              관능평가와 예측값 비교
            </Typography>

            <Box display="flex" justifyContent="center" sx={{ my: 2 }}>
              <RadarChart
                outerRadius={110}
                width={360}
                height={300}
                data={chartData}
              >
                <PolarGrid />
                <PolarAngleAxis dataKey="항목" tick={{ fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, 10]} />
                {(selectedChart === 'prediction' || selectedChart === 'both') && (
                  <Radar
                    name="예측값"
                    dataKey="예측값"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.6}
                  />
                )}
                {(selectedChart === 'sensory' || selectedChart === 'both') && (
                  <Radar
                    name="관능평가"
                    dataKey="관능평가"
                    stroke="#82ca9d"
                    fill="#82ca9d"
                    fillOpacity={0.6}
                  />
                )}
                <Legend
                  wrapperStyle={{ marginBottom: '-20px', fontSize: '12px' }}
                  payload={[
                    { value: '예측값', type: 'rect', color: '#8884d8' },
                    { value: '관능평가', type: 'rect', color: '#82ca9d' },
                  ]}
                />
              </RadarChart>
            </Box>

            {/* 그래프 토글 버튼 */}
            <Box
              display="flex"
              justifyContent="center"
              gap={2}
              sx={{ mt: 3, mb: 3 }}
            >
              <Chip
                label="관능평가"
                onClick={() => handleChartToggle('sensory')}
                variant={selectedChart === 'sensory' ? 'filled' : 'outlined'}
                color={selectedChart === 'sensory' ? 'primary' : 'default'}
                sx={{
                  minWidth: 80,
                  fontWeight: selectedChart === 'sensory' ? 'bold' : 'normal',
                  backgroundColor:
                    selectedChart === 'sensory' ? '#82ca9d' : 'transparent',
                  color: selectedChart === 'sensory' ? 'white' : '#82ca9d',
                  borderColor: '#82ca9d',
                  '&:hover': {
                    backgroundColor:
                      selectedChart === 'sensory' ? '#6eb885' : '#f0fff0',
                  },
                }}
              />
              <Chip
                label="예측값"
                onClick={() => handleChartToggle('prediction')}
                variant={selectedChart === 'prediction' ? 'filled' : 'outlined'}
                color={selectedChart === 'prediction' ? 'primary' : 'default'}
                sx={{
                  minWidth: 80,
                  fontWeight: selectedChart === 'prediction' ? 'bold' : 'normal',
                  backgroundColor:
                    selectedChart === 'prediction' ? '#8884d8' : 'transparent',
                  color: selectedChart === 'prediction' ? 'white' : '#8884d8',
                  borderColor: '#8884d8',
                  '&:hover': {
                    backgroundColor:
                      selectedChart === 'prediction' ? '#7070c7' : '#f0f0ff',
                  },
                }}
              />

              <Chip
                label="전체"
                onClick={() => handleChartToggle('both')}
                variant={selectedChart === 'both' ? 'filled' : 'outlined'}
                color={selectedChart === 'both' ? 'primary' : 'default'}
                sx={{
                  minWidth: 80,
                  fontWeight: selectedChart === 'both' ? 'bold' : 'normal',
                  backgroundColor:
                    selectedChart === 'both' ? '#666666' : 'transparent',
                  color: selectedChart === 'both' ? 'white' : '#666666',
                  borderColor: '#666666',
                  '&:hover': {
                    backgroundColor:
                      selectedChart === 'both' ? '#555555' : '#f5f5f5',
                  },
                }}
              />
            </Box>

            {showTableComparison && (
              <Box mt={4}>
                <Typography variant="subtitle2" gutterBottom>
                  수치 비교 표
                </Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>항목</TableCell>
                        <TableCell align="right">예측값</TableCell>
                        <TableCell align="right">오차</TableCell>
                        <TableCell align="center">관능평가</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {chartData.map((row) => {
                        const prediction = row.예측값;
                        const sensory = row.관능평가;
                        let difference = 1;
                        let differenceColor = 'black';

                        if (prediction !== null && sensory !== null) {
                          difference = prediction - sensory;
                          if (difference > 0) {
                            differenceColor = 'red'; // 예측값이 더 높음
                          } else if (difference < 0) {
                            differenceColor = 'blue'; // 관능평가가 더 높음
                          }
                          // difference === 0이면 검은색 (기본값)
                        }

                        return (
                          <TableRow key={row.항목}>
                            <TableCell>{row.항목}</TableCell>
                            <TableCell align="right">
                              {prediction !== null ? prediction.toFixed(1) : '-'}
                            </TableCell>
                            <TableCell
                              align="right"
                              sx={{ color: differenceColor, fontSize: '11px' }}
                            >
                              {prediction !== null && sensory !== null
                                ? difference.toFixed(1)
                                : '-'}
                            </TableCell>
                            <TableCell align="center">
                              {sensory !== null ? sensory.toFixed(1) : '-'}
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </>
        ) : (
          renderXAIContent()
        )}
      </DialogContent>

      <DialogActions>
        <Button
          onClick={onClose}
          variant="contained"
          sx={{
            backgroundColor: '#4caf50',
            '&:hover': {
              backgroundColor: '#45a049',
            },
          }}
        >
          닫기
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PredictionDetailPanel;
