import React, { useState } from 'react';
import {
  Box,
  Typography,
  IconButton,
  LinearProgress,
  Chip,
  Collapse,
  Paper,
  Button,
  Tooltip,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Close as CloseIcon,
  Minimize as MinimizeIcon,
  OpenInFull as OpenInFullIcon,
} from '@mui/icons-material';

const navy = '#0F3659';

const PredictionProgressModal = ({
  open,
  onClose,
  progress = [],
  totalCount = 0,
  isCompleted = false,
  title = '예측 진행 상황',
}) => {
  const [expandedItems, setExpandedItems] = useState(new Set());
  const [showDetails, setShowDetails] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);

  // 진행률 계산
  const completedCount = progress.filter(
    (item) => item.status === 'completed'
  ).length;
  const failedCount = progress.filter(
    (item) => item.status === 'failed'
  ).length;
  const pendingCount = progress.filter(
    (item) => item.status === 'pending'
  ).length;

  // 실제 예측할 항목 수 계산 (seqno와 isRefrigerated가 있는 항목들)
  const actualTotalCount = progress.filter(
    (item) => item.seqno !== null && item.isRefrigerated !== null
  ).length;

  const progressPercentage =
    actualTotalCount > 0 ? (completedCount / actualTotalCount) * 100 : 0;

  // 상태별 색상 및 아이콘
  const getStatusInfo = (status) => {
    switch (status) {
      case 'completed':
        return { color: 'success', icon: <CheckCircleIcon />, label: '완료' };
      case 'failed':
        return { color: 'error', icon: <ErrorIcon />, label: '실패' };
      case 'pending':
        return { color: 'warning', icon: <PendingIcon />, label: '대기중' };
      default:
        return { color: 'default', icon: <PendingIcon />, label: '알 수 없음' };
    }
  };

  // 아이템 확장/축소 토글
  const toggleItemExpansion = (itemId) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  // 상세 정보 표시 토글
  const toggleDetails = () => {
    setShowDetails(!showDetails);
  };

  // 최소화/최대화 토글
  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  // 상태별 요약 정보
  const getSummaryText = () => {
    if (isCompleted) {
      if (failedCount > 0) {
        return `${completedCount}개 완료, ${failedCount}개 실패`;
      }
      return `${completedCount}개 모두 완료!`;
    }

    // 진행 중일 때 더 자세한 정보 표시
    if (actualTotalCount > 0) {
      if (completedCount === 0) {
        return `${actualTotalCount}개 항목 준비 중...`;
      } else if (completedCount < actualTotalCount) {
        return `${completedCount}/${actualTotalCount} 진행중...`;
      }
    }

    return `${completedCount}/${totalCount} 진행중...`;
  };

  // 상태별 배경색
  const getStatusBackgroundColor = (status) => {
    switch (status) {
      case 'completed':
        return '#e8f5e9';
      case 'failed':
        return '#ffebee';
      case 'pending':
        return '#fff3e0';
      default:
        return '#f5f5f5';
    }
  };

  if (!open) return null;

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 20,
        right: 20,
        zIndex: 9999,
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
            {progressPercentage.toFixed(0)}%
          </Typography>
          <LinearProgress
            variant="determinate"
            value={progressPercentage}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: '#e0e0e0',
              '& .MuiLinearProgress-bar': {
                backgroundColor: failedCount > 0 ? '#ff9800' : '#4caf50',
                borderRadius: 4,
              },
            }}
          />
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mt: 1, display: 'block' }}
          >
            {getSummaryText()}
          </Typography>
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ display: 'block', mt: 0.5 }}
          >
            총 {actualTotalCount}개 항목
          </Typography>
        </Box>
      </Collapse>

      {/* 최대화된 상태 */}
      <Collapse in={!isMinimized}>
        <Box sx={{ p: 2, maxHeight: '70vh', overflow: 'auto' }}>
          {/* 전체 진행률 */}
          <Box sx={{ mb: 2 }}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                mb: 1,
              }}
            >
              <Typography variant="subtitle2" sx={{ color: navy }}>
                전체 진행률
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {getSummaryText()}
              </Typography>
            </Box>

            <LinearProgress
              variant="determinate"
              value={progressPercentage}
              sx={{
                height: 10,
                borderRadius: 5,
                backgroundColor: '#e0e0e0',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: failedCount > 0 ? '#ff9800' : '#4caf50',
                  borderRadius: 5,
                },
              }}
            />

            <Box
              sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}
            >
              <Typography variant="caption" color="text.secondary">
                진행률: {progressPercentage.toFixed(1)}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {completedCount} / {actualTotalCount}
              </Typography>
            </Box>
          </Box>

          {/* 상태별 요약 칩 */}
          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            <Chip
              icon={<CheckCircleIcon />}
              label={`완료: ${completedCount}`}
              size="small"
              color="success"
              variant="outlined"
            />
            {failedCount > 0 && (
              <Chip
                icon={<ErrorIcon />}
                label={`실패: ${failedCount}`}
                size="small"
                color="error"
                variant="outlined"
              />
            )}
            {pendingCount > 0 && (
              <Chip
                icon={<PendingIcon />}
                label={`대기중: ${pendingCount}`}
                size="small"
                color="warning"
                variant="outlined"
              />
            )}
          </Box>

          {/* 상세 진행 상황 */}
          <Collapse in={showDetails || !isCompleted}>
            <Paper sx={{ p: 1.5, bgcolor: '#fafafa' }}>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  mb: 1,
                }}
              >
                <Typography
                  variant="subtitle2"
                  sx={{ color: navy, fontSize: '0.9rem' }}
                >
                  개별 진행 상황
                </Typography>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={toggleDetails}
                  sx={{ fontSize: '0.7rem', py: 0.25, px: 1 }}
                >
                  {showDetails ? '접기' : '펼치기'}
                </Button>
              </Box>

              <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                {progress.map((item, index) => {
                  const statusInfo = getStatusInfo(item.status);
                  const isExpanded = expandedItems.has(item.id);

                  return (
                    <Box
                      key={item.id || index}
                      sx={{
                        border: '1px solid #e0e0e0',
                        borderRadius: 1,
                        mb: 0.5,
                        bgcolor: getStatusBackgroundColor(item.status),
                        p: 1,
                      }}
                    >
                      <Box
                        sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                        }}
                      >
                        <Box
                          sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
                        >
                          <Box sx={{ color: statusInfo.color }}>
                            {statusInfo.icon}
                          </Box>
                          <Typography
                            variant="caption"
                            sx={{ fontWeight: 'medium' }}
                          >
                            {item.id || `항목 ${index + 1}`}
                          </Typography>
                        </Box>
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
                            sx={{ height: 20, fontSize: '0.6rem' }}
                          />
                          <IconButton
                            size="small"
                            onClick={() =>
                              toggleItemExpansion(item.id || index)
                            }
                            sx={{ p: 0.25 }}
                          >
                            {isExpanded ? (
                              <ExpandLessIcon fontSize="small" />
                            ) : (
                              <ExpandMoreIcon fontSize="small" />
                            )}
                          </IconButton>
                        </Box>
                      </Box>

                      {/* 확장 가능한 상세 정보 */}
                      <Collapse in={isExpanded}>
                        <Box
                          sx={{
                            mt: 1,
                            p: 1,
                            bgcolor: 'white',
                            borderRadius: 1,
                          }}
                        >
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ display: 'block', mb: 0.5 }}
                          >
                            {item.seqno !== undefined && `Seqno: ${item.seqno}`}
                            {item.isRefrigerated !== undefined &&
                              ` | ${item.isRefrigerated ? '숙성' : '냉장'}`}
                          </Typography>
                          {item.message && (
                            <Typography
                              variant="caption"
                              color="text.secondary"
                              sx={{ display: 'block', mb: 0.5 }}
                            >
                              상태: {item.message}
                            </Typography>
                          )}
                          {item.error && (
                            <Typography
                              variant="caption"
                              color="error"
                              sx={{ display: 'block' }}
                            >
                              오류: {item.error}
                            </Typography>
                          )}
                          {item.completedAt && (
                            <Typography
                              variant="caption"
                              color="text.secondary"
                              sx={{ display: 'block' }}
                            >
                              완료시간:{' '}
                              {new Date(item.completedAt).toLocaleString()}
                            </Typography>
                          )}
                          {item.predictions && (
                            <Box sx={{ mt: 0.5 }}>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                예측값:{' '}
                                {item.predictions
                                  .map((p) => p.toFixed(2))
                                  .join(', ')}
                              </Typography>
                            </Box>
                          )}
                        </Box>
                      </Collapse>
                    </Box>
                  );
                })}
              </Box>
            </Paper>
          </Collapse>

          {/* 완료 메시지 */}
          {isCompleted && (
            <Box
              sx={{
                mt: 2,
                p: 1.5,
                bgcolor: '#e8f5e9',
                borderRadius: 1,
                textAlign: 'center',
              }}
            >
              <Typography
                variant="subtitle2"
                sx={{ color: 'success.main', mb: 0.5 }}
              >
                🎉 예측이 완료되었습니다!
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {failedCount > 0
                  ? `${completedCount}개 항목의 예측이 완료되었습니다. ${failedCount}개 항목에서 오류가 발생했습니다.`
                  : `모든 ${completedCount}개 항목의 예측이 성공적으로 완료되었습니다.`}
              </Typography>
            </Box>
          )}
        </Box>
      </Collapse>
    </Box>
  );
};

export default PredictionProgressModal;
