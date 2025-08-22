import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material';
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  ZoomIn as ZoomInIcon,
} from '@mui/icons-material';

const navy = '#0F3659';

// 라벨 매핑 (API 응답 순서와 정확히 매칭)
const LABELS = [
  '마블링(Marbling)', // predictions[0], xai_image_urls[0]
  '육색(Meat Color)', // predictions[1], xai_image_urls[1]
  '조직감(Texture)', // predictions[2], xai_image_urls[2]
  '표면육즙(Surface Moisture)', // predictions[3], xai_image_urls[3]
  '전체 기호도(Overall)', // predictions[4], xai_image_urls[4]
];

// 파일명에서 라벨 추출하는 함수
const getLabelFromFilename = (filename) => {
  if (!filename) return '알 수 없음';

  if (filename.includes('Marbling')) return '마블링(Marbling)';
  if (filename.includes('Meat_Color')) return '육색(Meat Color)';
  if (filename.includes('Texture')) return '조직감(Texture)';
  if (filename.includes('Surface_Moisture'))
    return '표면육즙(Surface Moisture)';
  if (filename.includes('Total')) return '전체 기호도(Overall)';

  return '알 수 없음';
};

const XAIViewer = ({
  open,
  onClose,
  xaiImageUrls = [],
  predictions = [],
  title = 'XAI 분석 결과',
  initialTabIndex = 0, // 초기 탭 인덱스 추가
}) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(initialTabIndex);
  const [isZoomed, setIsZoomed] = useState(false);

  // S3 base URL
  const S3_BASE_URL =
    'https://test-deeplant-bucket.s3.ap-northeast-2.amazonaws.com/';

  // 이미지 URL을 완전한 S3 URL로 변환
  const getFullImageUrl = (imagePath) => {
    if (!imagePath) return '';

    // 이미 완전한 URL인 경우 그대로 반환
    if (imagePath.startsWith('http')) {
      return imagePath;
    }

    // s3:// 경로를 https:// 경로로 변환
    if (imagePath.startsWith('s3://')) {
      return imagePath.replace('s3://test-deeplant-bucket/', S3_BASE_URL);
    }

    // 상대 경로인 경우 S3 base URL과 결합
    return S3_BASE_URL + imagePath;
  };

  const handlePrevious = () => {
    setCurrentImageIndex((prev) =>
      prev === 0 ? xaiImageUrls.length - 1 : prev - 1
    );
  };

  const handleNext = () => {
    setCurrentImageIndex((prev) =>
      prev === xaiImageUrls.length - 1 ? 0 : prev + 1
    );
  };

  const handleImageClick = () => {
    setIsZoomed(!isZoomed);
  };

  const handleClose = () => {
    setIsZoomed(false);
    setCurrentImageIndex(0);
    onClose();
  };

  // initialTabIndex가 변경되면 currentImageIndex도 업데이트
  useEffect(() => {
    if (open && initialTabIndex >= 0 && initialTabIndex < xaiImageUrls.length) {
      setCurrentImageIndex(initialTabIndex);
    }
  }, [open, initialTabIndex, xaiImageUrls.length]);

  if (!open || !xaiImageUrls || xaiImageUrls.length === 0) {
    return null;
  }

  const currentImageUrl = getFullImageUrl(xaiImageUrls[currentImageIndex]);
  const currentLabel = getLabelFromFilename(xaiImageUrls[currentImageIndex]);
  const currentPrediction = predictions[currentImageIndex];

  return (
    <>
      {/* 메인 XAI 뷰어 */}
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle sx={{ color: navy, borderBottom: `1px solid ${navy}` }}>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <Typography variant="h6">{title}</Typography>
            <IconButton onClick={handleClose} size="small">
              <Button variant="outlined" size="small">
                닫기
              </Button>
            </IconButton>
          </Box>
        </DialogTitle>

        <DialogContent sx={{ p: 3 }}>
          {/* 현재 이미지 정보 */}
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="h6" sx={{ color: navy, mb: 1 }}>
              {currentLabel}
            </Typography>
            {currentPrediction !== undefined && (
              <Typography variant="body1" sx={{ color: 'text.secondary' }}>
                예측값: {currentPrediction.toFixed(2)}
              </Typography>
            )}
            <Typography
              variant="caption"
              sx={{ color: 'text.secondary', display: 'block', mt: 1 }}
            >
              {currentImageIndex + 1} / {xaiImageUrls.length}
            </Typography>
          </Box>

          {/* 이미지 표시 영역 */}
          <Box
            sx={{
              position: 'relative',
              height: 400,
              border: '1px solid #ddd',
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              bgcolor: '#fafafa',
              mb: 2,
              cursor: 'pointer',
            }}
            onClick={handleImageClick}
          >
            {currentImageUrl ? (
              <img
                src={currentImageUrl}
                alt={currentLabel}
                style={{
                  maxWidth: '100%',
                  maxHeight: '100%',
                  objectFit: 'contain',
                  borderRadius: 8,
                }}
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'block';
                }}
              />
            ) : null}

            {/* 이미지 로드 실패 시 표시 */}
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{
                display: currentImageUrl ? 'none' : 'block',
                textAlign: 'center',
              }}
            >
              이미지를 불러올 수 없습니다
            </Typography>

            {/* 줌 아이콘 */}
            <Box
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                bgcolor: 'rgba(255,255,255,0.8)',
                borderRadius: '50%',
                p: 0.5,
              }}
            >
              <ZoomInIcon fontSize="small" />
            </Box>
          </Box>

          {/* 네비게이션 컨트롤 */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <IconButton
              onClick={handlePrevious}
              disabled={xaiImageUrls.length <= 1}
              sx={{ color: navy }}
            >
              <ChevronLeftIcon />
            </IconButton>

            {/* 이미지 인덱스 버튼들 */}
            <Box
              sx={{
                display: 'flex',
                gap: 0.5,
                flexWrap: 'wrap',
                justifyContent: 'center',
              }}
            >
              {xaiImageUrls.map((url, idx) => (
                <Button
                  key={idx}
                  size="small"
                  variant={currentImageIndex === idx ? 'contained' : 'outlined'}
                  onClick={() => setCurrentImageIndex(idx)}
                  sx={{
                    minWidth: 'auto',
                    px: 1,
                    py: 0.5,
                    fontSize: '0.75rem',
                    backgroundColor:
                      currentImageIndex === idx ? navy : 'transparent',
                    '&:hover': {
                      backgroundColor:
                        currentImageIndex === idx
                          ? navy
                          : 'rgba(15, 54, 89, 0.1)',
                    },
                  }}
                >
                  {getLabelFromFilename(url).split('(')[0]}
                </Button>
              ))}
            </Box>

            <IconButton
              onClick={handleNext}
              disabled={xaiImageUrls.length <= 1}
              sx={{ color: navy }}
            >
              <ChevronRightIcon />
            </IconButton>
          </Box>

          {/* 예측값 요약 */}
          {predictions.length > 0 && (
            <Box sx={{ mt: 3, p: 2, bgcolor: '#f8f9fa', borderRadius: 2 }}>
              <Typography variant="subtitle2" sx={{ color: navy, mb: 1 }}>
                예측값 요약
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {xaiImageUrls.map((url, idx) => (
                  <Chip
                    key={idx}
                    label={`${getLabelFromFilename(url).split('(')[0]}: ${predictions[idx]?.toFixed(2) || 'N/A'}`}
                    size="small"
                    variant="outlined"
                    sx={{
                      borderColor: navy,
                      color: navy,
                      '&:hover': { bgcolor: 'rgba(15, 54, 89, 0.1)' },
                    }}
                  />
                ))}
              </Box>
            </Box>
          )}
        </DialogContent>

        <DialogActions sx={{ p: 2, borderTop: `1px solid #eee` }}>
          <Button onClick={handleClose} variant="outlined">
            닫기
          </Button>
        </DialogActions>
      </Dialog>

      {/* 줌된 이미지 모달 */}
      <Dialog
        open={isZoomed}
        onClose={() => setIsZoomed(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle sx={{ color: navy }}>
          {currentLabel} - 확대 보기
        </DialogTitle>
        <DialogContent>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              minHeight: 500,
            }}
          >
            {currentImageUrl && (
              <img
                src={currentImageUrl}
                alt={currentLabel}
                style={{
                  maxWidth: '100%',
                  maxHeight: '100%',
                  objectFit: 'contain',
                }}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsZoomed(false)} variant="outlined">
            닫기
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default XAIViewer;
