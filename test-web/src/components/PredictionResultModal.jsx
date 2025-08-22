import React, { useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Chip,
  Collapse,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Paper,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  ExpandMore as ExpandMoreIcon,
  Close as CloseIcon,
  Image as ImageIcon,
  Minimize as MinimizeIcon,
  OpenInFull as OpenInFullIcon,
} from '@mui/icons-material';
import XAIViewer from './XAIViewer';

const navy = '#0F3659';

// 라벨 매핑 (예측 결과 순서에 맞춤)
const LABELS = [
  '마블링(Marbling)',
  '육색(Meat Color)',
  '조직감(Texture)',
  '표면육즙(Surface Moisture)',
  '전체 기호도(Overall)',
];

const PredictionResultModal = ({
  open,
  onClose,
  results = [],
  title = '예측 결과',
}) => {
  const [selectedItem, setSelectedItem] = useState(null);
  const [xaiViewerOpen, setXaiViewerOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);

  // 결과를 ID별로 그룹화
  const groupedResults = results.reduce((acc, result) => {
    const key = result.id;
    if (!acc[key]) {
      acc[key] = [];
    }
    acc[key].push(result);
    return acc;
  }, {});

  // XAI 뷰어 열기
  const handleOpenXAI = (item) => {
    setSelectedItem(item);
    setXaiViewerOpen(true);
  };

  // XAI 뷰어 닫기
  const handleCloseXAI = () => {
    setXaiViewerOpen(false);
    setSelectedItem(null);
  };

  // 최소화/최대화 토글
  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  // 상태별 색상 및 아이콘
  const getStatusInfo = (status) => {
    switch (status) {
      case 'completed':
        return { color: 'success', icon: <CheckCircleIcon />, label: '성공' };
      case 'failed':
        return { color: 'error', icon: <ErrorIcon />, label: '실패' };
      default:
        return { color: 'default', icon: <CheckCircleIcon />, label: '완료' };
    }
  };

  // 예측값을 라벨과 함께 표시
  const renderPredictions = (predictions) => {
    if (!predictions || predictions.length === 0) return '예측값 없음';

    return (
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
        {predictions.map((pred, idx) => (
          <Chip
            key={idx}
            label={`${LABELS[idx]?.split('(')[0] || `항목${idx + 1}`}: ${pred.toFixed(2)}`}
            size="small"
            variant="outlined"
            sx={{
              borderColor: navy,
              color: navy,
              fontSize: '0.7rem',
              height: 'auto',
              '& .MuiChip-label': { py: 0.5 },
            }}
          />
        ))}
      </Box>
    );
  };

  // 날짜 포맷팅
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleString('ko-KR');
    } catch {
      return dateString;
    }
  };

  if (!open) return null;

  return (
    <>
      <Box
        sx={{
          position: 'fixed',
          top: 20,
          right: isMinimized ? 20 : 340, // 진행 상황 모달과 겹치지 않도록
          zIndex: 9998,
          width: isMinimized ? 300 : 400,
          maxHeight: isMinimized ? 'auto' : '80vh',
          backgroundColor: 'white',
          border: `2px solid ${navy}`,
          borderRadius: 2,
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
          overflow: 'hidden',
          transition: 'all 0.3s ease',
        }}
      >
        {/* 헤더 */}
        <Box
          sx={{
            backgroundColor: navy,
            color: 'white',
            p: 1,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            cursor: 'move',
          }}
        >
          <Typography variant="subtitle2" sx={{ fontWeight: 'medium' }}>
            {title}
          </Typography>
          <Box sx={{ display: 'flex', gap: 0.5 }}>
            <Tooltip title={isMinimized ? '최대화' : '최소화'}>
              <IconButton
                size="small"
                onClick={toggleMinimize}
                sx={{ color: 'white', p: 0.5 }}
              >
                {isMinimized ? (
                  <OpenInFullIcon fontSize="small" />
                ) : (
                  <MinimizeIcon fontSize="small" />
                )}
              </IconButton>
            </Tooltip>
            <Tooltip title="닫기">
              <IconButton
                size="small"
                onClick={onClose}
                sx={{ color: 'white', p: 0.5 }}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* 최소화된 상태 */}
        <Collapse in={isMinimized}>
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" sx={{ color: navy, mb: 1 }}>
              🎉 완료!
            </Typography>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ display: 'block', mb: 1 }}
            >
              총 {Object.keys(groupedResults).length}개 그룹
            </Typography>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ display: 'block' }}
            >
              {results.filter((r) => r.status !== 'failed').length}개 성공
              {results.some((r) => r.status === 'failed') &&
                `, ${results.filter((r) => r.status === 'failed').length}개 실패`}
            </Typography>
          </Box>
        </Collapse>

        {/* 최대화된 상태 */}
        <Collapse in={!isMinimized}>
          <Box sx={{ p: 2, maxHeight: '70vh', overflow: 'auto' }}>
            {/* 요약 정보 */}
            <Paper sx={{ p: 1.5, mb: 2, bgcolor: '#f8f9fa' }}>
              <Typography variant="subtitle2" sx={{ color: navy, mb: 1 }}>
                예측 완료 요약
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={`총 ${Object.keys(groupedResults).length}개 그룹`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
                <Chip
                  label={`총 ${results.length}개 항목`}
                  size="small"
                  color="secondary"
                  variant="outlined"
                />
                <Chip
                  label={`성공: ${results.filter((r) => r.status !== 'failed').length}개`}
                  size="small"
                  color="success"
                  variant="outlined"
                />
                {results.some((r) => r.status === 'failed') && (
                  <Chip
                    label={`실패: ${results.filter((r) => r.status === 'failed').length}개`}
                    size="small"
                    color="error"
                    variant="outlined"
                  />
                )}
              </Box>
            </Paper>

            {/* 결과 목록 */}
            <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
              {Object.entries(groupedResults).map(([groupId, groupItems]) => (
                <Accordion key={groupId} sx={{ mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        width: '100%',
                      }}
                    >
                      <Box sx={{ color: 'success.main' }}>
                        <CheckCircleIcon fontSize="small" />
                      </Box>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography
                          variant="caption"
                          sx={{ fontWeight: 'medium' }}
                        >
                          ID: {groupId}
                        </Typography>
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{ display: 'block' }}
                        >
                          {groupItems.length}개 항목 |{' '}
                          {formatDate(groupItems[0]?.created_at)}
                        </Typography>
                      </Box>
                      <Chip
                        label={`${groupItems.length}개`}
                        size="small"
                        color="primary"
                        variant="outlined"
                        sx={{ height: 20, fontSize: '0.6rem' }}
                      />
                    </Box>
                  </AccordionSummary>

                  <AccordionDetails sx={{ p: 1 }}>
                    <Box
                      sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        gap: 0.5,
                      }}
                    >
                      {groupItems.map((item, index) => {
                        const statusInfo = getStatusInfo(item.status);

                        return (
                          <Box
                            key={`${groupId}-${index}`}
                            sx={{
                              border: '1px solid #e0e0e0',
                              borderRadius: 1,
                              p: 1,
                              bgcolor:
                                item.status === 'failed'
                                  ? '#ffebee'
                                  : '#f8f9fa',
                            }}
                          >
                            <Box
                              sx={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                              }}
                            >
                              <Typography
                                variant="caption"
                                sx={{ fontWeight: 'medium' }}
                              >
                                항목 {index + 1}
                              </Typography>
                              <Box
                                sx={{
                                  display: 'flex',
                                  gap: 0.5,
                                  alignItems: 'center',
                                }}
                              >
                                <Chip
                                  label={statusInfo.label}
                                  size="small"
                                  color={statusInfo.color}
                                  variant="outlined"
                                  sx={{ height: 18, fontSize: '0.6rem' }}
                                />
                                {item.xai_image_urls &&
                                  item.xai_image_urls.length > 0 && (
                                    <Button
                                      size="small"
                                      variant="outlined"
                                      startIcon={<ImageIcon />}
                                      onClick={() => handleOpenXAI(item)}
                                      sx={{
                                        borderColor: navy,
                                        color: navy,
                                        fontSize: '0.6rem',
                                        py: 0.25,
                                        px: 0.5,
                                        height: 24,
                                      }}
                                    >
                                      XAI
                                    </Button>
                                  )}
                              </Box>
                            </Box>

                            {/* 기본 정보 */}
                            <Box sx={{ mt: 0.5, mb: 0.5 }}>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                                sx={{ display: 'block' }}
                              >
                                Seqno: {item.seqno ?? 'N/A'} |{' '}
                                {item.isRefrigerated ? '숙성' : '냉장'} |{' '}
                                {formatDate(item.created_at)}
                              </Typography>
                            </Box>

                            {/* 예측값 */}
                            <Box sx={{ mb: 0.5 }}>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                                sx={{ display: 'block', mb: 0.25 }}
                              >
                                예측 결과:
                              </Typography>
                              {renderPredictions(item.predictions)}
                            </Box>

                            {/* 오류 정보 */}
                            {item.error && (
                              <Box sx={{ mt: 0.5 }}>
                                <Typography variant="caption" color="error">
                                  오류: {item.error}
                                </Typography>
                              </Box>
                            )}
                          </Box>
                        );
                      })}
                    </Box>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>

            {/* 결과가 없을 때 */}
            {results.length === 0 && (
              <Box sx={{ textAlign: 'center', py: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  예측 결과가 없습니다.
                </Typography>
              </Box>
            )}
          </Box>
        </Collapse>
      </Box>

      {/* XAI 뷰어 */}
      {selectedItem && (
        <XAIViewer
          open={xaiViewerOpen}
          onClose={handleCloseXAI}
          xaiImageUrls={selectedItem.xai_image_urls || []}
          predictions={selectedItem.predictions || []}
          title={`XAI 분석 - ID: ${selectedItem.id}`}
        />
      )}
    </>
  );
};

export default PredictionResultModal;
