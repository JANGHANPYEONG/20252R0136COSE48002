import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Alert,
  Paper,
  Chip,
  Divider,
  TextField,
  Dialog,
  DialogContent,
  IconButton
} from '@mui/material';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import ImageIcon from '@mui/icons-material/Image';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import CloseIcon from '@mui/icons-material/Close';
import RefreshIcon from '@mui/icons-material/Refresh';
import ClearIcon from '@mui/icons-material/Clear';
import axios from 'axios';
import style from './style/dashboardstyle';

const navy = '#0F3659';

const XAI = () => {
  const [loading, setLoading] = useState(false);
  const [heatmapImages, setHeatmapImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [analysisStatus, setAnalysisStatus] = useState('ready'); // ready, processing, completed, error
  const [imagePath, setImagePath] = useState('');
  const [modelPath, setModelPath] = useState('./best_model.pt');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [alertInfo, setAlertInfo] = useState({ show: false, type: 'info', message: '' });
  const [analysisResult, setAnalysisResult] = useState(null);

  const showAlert = (type, message) => {
    setAlertInfo({ show: true, type, message });
    setTimeout(() => setAlertInfo({ show: false, type: 'info', message: '' }), 5000);
  };

  // Heat map 이미지 목록 로드
  const loadHeatmapImages = async () => {
    try {
      const response = await axios.get('/api/xai/heatmap-list');
      if (response.data.success) {
        setHeatmapImages(response.data.heatmapFiles.map((file, index) => ({
          id: index + 1,
          name: file.filename,
          url: file.url,
          path: file.path,
          size: file.size,
          timestamp: new Date(file.modified * 1000).toLocaleString()
        })));
      }
    } catch (error) {
      console.error('Heat map 이미지 로드 오류:', error);
      showAlert('error', 'Heat map 이미지 로드에 실패했습니다.');
    }
  };

  // XAI 분석 실행
  const runXAIAnalysis = async () => {
    if (!imagePath.trim()) {
      showAlert('warning', '이미지 폴더 경로를 입력해주세요.');
      return;
    }

    setLoading(true);
    setAnalysisStatus('processing');
    setAnalysisResult(null);
    
    try {
      const response = await axios.post('/api/xai/run-analysis', {
        imagePath: imagePath.trim(),
        modelPath: modelPath.trim()
      });

      if (response.data.success) {
        setAnalysisStatus('completed');
        setAnalysisResult(response.data);
        showAlert('success', `XAI 분석이 완료되었습니다. ${response.data.heatmapFiles.length}개의 heat map이 생성되었습니다.`);
        await loadHeatmapImages();
      } else {
        setAnalysisStatus('error');
        showAlert('error', response.data.error || 'XAI 분석에 실패했습니다.');
      }
    } catch (error) {
      console.error('XAI 분석 오류:', error);
      setAnalysisStatus('error');
      const errorMessage = error.response?.data?.error || error.message || 'XAI 분석 중 오류가 발생했습니다.';
      showAlert('error', errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Heat map 삭제
  const clearHeatmaps = async () => {
    try {
      const response = await axios.post('/api/xai/clear-heatmaps');
      if (response.data.success) {
        setHeatmapImages([]);
        setAnalysisResult(null);
        setAnalysisStatus('ready');
        setSelectedImage(null);
        showAlert('info', `${response.data.deletedCount}개의 heat map이 삭제되었습니다.`);
      }
    } catch (error) {
      showAlert('error', 'Heat map 삭제에 실패했습니다.');
      console.error('Heat map 삭제 오류:', error);
    }
  };

  // 이미지 클릭 시 다이얼로그 열기
  const openImageDialog = (image) => {
    setSelectedImage(image);
    setDialogOpen(true);
  };

  useEffect(() => {
    loadHeatmapImages();
  }, []);

  return (
    <Box sx={{ width: '100%', maxWidth: '1200px', margin: '20px auto', p: 3 }}>
      {/* 제목 */}
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="h4"
          sx={{ 
            color: navy, 
            fontWeight: '600'
          }}
        >
          XAI 분석
        </Typography>
        <Typography variant="body1" sx={{ mt: 1, color: '#666' }}>
          AI 모델의 예측 결과를 시각적으로 설명하는 Heat Map을 생성합니다.
        </Typography>
      </Box>

      {/* 알림 */}
      {alertInfo.show && (
        <Alert severity={alertInfo.type} sx={{ mb: 3 }}>
          {alertInfo.message}
        </Alert>
      )}

      {/* 상태 표시 */}
      {analysisStatus === 'processing' && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CircularProgress size={20} />
            XAI 분석이 진행 중입니다. 잠시만 기다려주세요...
          </Box>
        </Alert>
      )}

      {analysisStatus === 'completed' && analysisResult && (
        <Alert severity="success" sx={{ mb: 3 }}>
          XAI 분석이 완료되었습니다. {analysisResult.heatmapFiles.length}개의 Heat map 이미지가 생성되었습니다.
        </Alert>
      )}

      {analysisStatus === 'error' && (
        <Alert severity="error" sx={{ mb: 3 }}>
          XAI 분석 중 오류가 발생했습니다. 다시 시도해주세요.
        </Alert>
      )}

      {/* 제어 패널 */}
      <Paper elevation={1} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" sx={{ mb: 2, color: navy }}>
          분석 설정
        </Typography>
        
        {/* 입력 필드들 */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="이미지 폴더 경로"
              value={imagePath}
              onChange={(e) => setImagePath(e.target.value)}
              placeholder="예: ./data/images/sample"
              helperText="분석할 멀티밴드 이미지가 있는 폴더 경로"
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="모델 경로"
              value={modelPath}
              onChange={(e) => setModelPath(e.target.value)}
              placeholder="./best_model.pt"
              helperText="SpectrumNet 모델 파일 경로"
              disabled={loading}
            />
          </Grid>
        </Grid>

        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            onClick={runXAIAnalysis}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <AnalyticsIcon />}
            sx={{
              backgroundColor: navy,
              '&:hover': { backgroundColor: '#0a2a4a' },
            }}
          >
            {loading ? 'XAI 분석 중...' : 'XAI 분석 실행'}
          </Button>
          
          <Button
            variant="outlined"
            onClick={loadHeatmapImages}
            disabled={loading}
            startIcon={<RefreshIcon />}
          >
            새로고침
          </Button>
          
          <Button
            variant="outlined"
            onClick={clearHeatmaps}
            disabled={loading}
            startIcon={<ClearIcon />}
            color="error"
          >
            삭제
          </Button>
          
          <Chip 
            label={`상태: ${
              analysisStatus === 'ready' ? '대기' :
              analysisStatus === 'processing' ? '진행중' :
              analysisStatus === 'completed' ? '완료' : '오류'
            }`}
            color={
              analysisStatus === 'completed' ? 'success' :
              analysisStatus === 'processing' ? 'warning' :
              analysisStatus === 'error' ? 'error' : 'default'
            }
          />
        </Box>
      </Paper>

      <Divider sx={{ mb: 4 }} />

      {/* Heat map 이미지 갤러리 */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" sx={{ mb: 3, color: navy, display: 'flex', alignItems: 'center', gap: 1 }}>
          <ImageIcon />
          생성된 Heat Map 이미지 ({heatmapImages.length}개)
        </Typography>

        {heatmapImages.length === 0 ? (
          <Paper elevation={1} sx={{ p: 4, textAlign: 'center', backgroundColor: '#f8f9fa' }}>
            <ImageIcon sx={{ fontSize: 48, color: '#ccc', mb: 2 }} />
            <Typography variant="body1" color="textSecondary">
              아직 생성된 Heat map 이미지가 없습니다.
            </Typography>
            <Typography variant="body2" color="textSecondary">
              XAI 분석을 실행하여 Heat map을 생성해보세요.
            </Typography>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {heatmapImages.map((image) => (
              <Grid item xs={12} sm={6} md={4} key={image.id}>
                <Card 
                  sx={{ 
                    cursor: 'pointer',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 3
                    },
                    border: selectedImage?.id === image.id ? `2px solid ${navy}` : 'none'
                  }}
                  onClick={() => openImageDialog(image)}
                >
                  <Box sx={{ position: 'relative', paddingTop: '75%', backgroundColor: '#f5f5f5' }}>
                    <img
                      src={image.url}
                      alt={image.name}
                      style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover',
                        borderRadius: '4px 4px 0 0'
                      }}
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                    <Box
                      sx={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        display: 'none',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backgroundColor: '#e3f2fd'
                      }}
                    >
                      <ImageIcon sx={{ fontSize: 48, color: '#1976d2' }} />
                    </Box>
                  </Box>
                  <CardContent>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                      {image.name}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Chip 
                        label={`크기: ${(image.size / 1024).toFixed(1)}KB`}
                        size="small" 
                        color="primary" 
                        variant="outlined"
                      />
                      <Typography variant="caption" color="textSecondary">
                        {image.timestamp}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Box>

      {/* 분석 결과 정보 */}
      {analysisResult && (
        <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" sx={{ mb: 2, color: navy }}>
            분석 결과 정보
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>상태:</strong> {analysisResult.message}
              </Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>생성된 파일:</strong> {analysisResult.heatmapFiles.length}개
              </Typography>
              <Typography variant="body2">
                <strong>출력 폴더:</strong> {analysisResult.outputDir}
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* 이미지 확대 다이얼로그 */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogContent sx={{ p: 0, position: 'relative' }}>
          <IconButton
            onClick={() => setDialogOpen(false)}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              bgcolor: 'rgba(0,0,0,0.5)',
              color: 'white',
              zIndex: 1,
              '&:hover': {
                bgcolor: 'rgba(0,0,0,0.7)',
              }
            }}
          >
            <CloseIcon />
          </IconButton>
          {selectedImage && (
            <Box>
              <img
                src={selectedImage.url}
                alt={selectedImage.name}
                style={{
                  width: '100%',
                  height: 'auto',
                  display: 'block'
                }}
              />
              <Box sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                <Typography variant="h6" sx={{ mb: 1 }}>
                  {selectedImage.name}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  크기: {(selectedImage.size / 1024).toFixed(1)}KB | 생성 시간: {selectedImage.timestamp}
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default XAI;
