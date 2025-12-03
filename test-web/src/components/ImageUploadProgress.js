import React from 'react';
import { Box, LinearProgress, Typography, Paper } from '@mui/material';

/**
 * 이미지 업로드 진행 상황을 표시하는 컴포넌트
 * @param {Object} props - 컴포넌트 props
 * @param {boolean} props.show - 진행 바 표시 여부
 * @param {number} props.current - 현재 진행된 파일 수
 * @param {number} props.total - 전체 파일 수
 * @param {string} props.fileName - 현재 처리 중인 파일명
 * @param {string} props.stage - 현재 단계 ('processing', 'uploading', 'completed')
 */
const ImageUploadProgress = ({ 
  show = false, 
  current = 0, 
  total = 0, 
  fileName = '', 
  stage = 'processing' 
}) => {
  if (!show) return null;

  const progress = total > 0 ? (current / total) * 100 : 0;
  const isCompleted = stage === 'completed';

  const getStageText = () => {
    switch (stage) {
      case 'processing':
        return '이미지 처리 중...';
      case 'uploading':
        return '업로드 중...';
      case 'completed':
        return '업로드 완료!';
      default:
        return '처리 중...';
    }
  };

  const getProgressColor = () => {
    switch (stage) {
      case 'completed':
        return 'success';
      case 'uploading':
        return 'primary';
      case 'processing':
      default:
        return 'secondary';
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '400px',
        padding: 3,
        zIndex: 10000,
        backgroundColor: 'white',
        borderRadius: 2,
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
      }}
    >
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" sx={{ mb: 1, fontWeight: '600', color: '#0F3659' }}>
          {getStageText()}
        </Typography>
        
        <Typography variant="body2" sx={{ mb: 2, color: '#666' }}>
          {current} / {total} 파일 처리됨
        </Typography>

        <LinearProgress
          variant="determinate"
          value={progress}
          color={getProgressColor()}
          sx={{
            height: 8,
            borderRadius: 4,
            mb: 2,
            '& .MuiLinearProgress-bar': {
              borderRadius: 4,
            },
          }}
        />

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="body2" sx={{ color: '#666' }}>
            {Math.round(progress)}%
          </Typography>
          {isCompleted && (
            <Typography variant="body2" sx={{ color: '#28a745', fontWeight: '600' }}>
              ✅ 완료
            </Typography>
          )}
        </Box>

        {fileName && !isCompleted && (
          <Typography
            variant="body2"
            sx={{
              mt: 1,
              p: 1,
              backgroundColor: '#f8f9fa',
              borderRadius: 1,
              fontSize: '0.8rem',
              color: '#666',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            현재: {fileName}
          </Typography>
        )}
      </Box>
    </Paper>
  );
};

export default ImageUploadProgress;