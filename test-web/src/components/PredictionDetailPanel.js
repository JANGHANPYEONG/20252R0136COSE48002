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
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
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

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">예측 상세 정보 - {id}</Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
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
