import React from 'react';
import {
  Drawer, Box, Typography, IconButton, Divider, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, Legend, PolarRadiusAxis } from 'recharts';

const PredictionDetailPanel = ({ open, onClose, predictionData, labels = [], showTableComparison = false }) => {
  if (!predictionData) return null;
  const { id, prediction, sensory } = predictionData;

  // Recharts용 데이터 변환 (label 기준 정렬)
  const chartData = labels.map(key => ({
    항목: key,
    예측값: prediction?.[key] ?? null,
    관능평가: sensory?.[key] ?? null,
  }));

  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box sx={{ width: 400, padding: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">예측 상세 정보 - {id}</Typography>
          <IconButton onClick={onClose}><CloseIcon /></IconButton>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
          관능평가와 예측값 비교
        </Typography>

        <RadarChart outerRadius={110} width={350} height={300} data={chartData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="항목" tick={{ fontSize: 11 }} />
          <PolarRadiusAxis domain={[0, 10]} />
          <Radar name="예측값" dataKey="예측값" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
          <Radar name="관능평가" dataKey="관능평가" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
          <Legend wrapperStyle={{ marginBottom: '-20px', fontSize: '12px' }} />
        </RadarChart>
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
                        <TableCell align="right"></TableCell>
                        <TableCell align="left">관능평가</TableCell>
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
                                <TableCell align="right">{prediction !== null ? prediction.toFixed(1) : '-'}</TableCell>
                                <TableCell align="right" sx={{ color: differenceColor, fontSize: '11px'}}>
                                    {prediction !== null && sensory !== null ? difference.toFixed(1) : '-'}
                                </TableCell>
                                <TableCell align="left">{sensory !== null ? sensory.toFixed(1) : '-'}</TableCell>
                            </TableRow>
                        );
                    })}
                    </TableBody>
                </Table>
                </TableContainer>
            </Box>
            )}
      </Box>
    </Drawer>
  );
};

export default PredictionDetailPanel;
