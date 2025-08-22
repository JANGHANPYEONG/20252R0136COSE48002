// src/routes/MeatDetailPage.jsx
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Divider,
  Button,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  Stack,
  Snackbar,
  Alert,
} from '@mui/material';
import { useEffect, useState, useMemo } from 'react';
import { Tabs, Tab, ToggleButton, ToggleButtonGroup } from '@mui/material';
// MUI - 멀티셀렉트 UI
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  ListItemText,
  OutlinedInput,
} from '@mui/material';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { confirmMeat, rejectMeat } from '../API/updateDataStatus';
import { updateMeatInfo } from '../API/add/updateMeatInfo';
import useMeatDetail from '../API/meat/useMeatDetail'; // ✅ 새 API 훅
import { getSpectralInfo } from '../API/meat/getSpectralInfo'; // 파장 정보 API
import { apiIP } from '../config'; // API IP 주소
const navy = '#0F3659';

// ========================= 새 스키마 전용 라벨 세트 =========================
const LABELS = [
  { key: 'meat_color', name: '육색' },
  { key: 'marbling', name: '마블링' },
  { key: 'texture', name: '조직감' },
  { key: 'surface_moisture', name: '표면육즙' },
  { key: 'overall', name: '전체 기호도' },
];

// ========================= 정규화 어댑터 =========================
function normalizeItemFromBackend(src) {
  const idxId = src?.id ?? null; // 내부 index (이력+샘플)
  const traceId = src?.meat?.traceNum ?? null; // 실제 이력번호

  const seq0 = src?.by_seqno_and_condition?.find((x) => x.seqno === 0) ?? null; // period 0 (표기상 1일차로 사용)
  const seq1 = src?.by_seqno_and_condition?.find((x) => x.seqno === 1) ?? null; // period 7 (7일차)

  const pickEval = (e) =>
    e
      ? {
          meat_color: e.meat_color ?? null,
          marbling: e.marbling ?? null,
          texture: e.texture ?? null,
          surface_moisture: e.surface_moisture ?? null,
          overall: e.overall ?? null,
        }
      : null;

  const sensory = {
    1: pickEval(seq0?.sensory_eval),
    7: pickEval(seq1?.sensory_eval),
  };

  const prediction = {
    1: {
      RGB: pickEval(seq0?.ai_sensory_eval),
      MSI: pickEval(seq0?.hsi_sensory_eval),
    },
    7: {
      RGB: pickEval(seq1?.ai_sensory_eval),
      MSI: pickEval(seq1?.hsi_sensory_eval),
    },
  };

  // RGB 썸네일: 관능 촬영 이미지 경로 사용
  const images = {
    RGB: {
      0: seq0?.sensory_eval?.imagePath ?? null,
      7: seq1?.sensory_eval?.imagePath ?? null,
    },
    MSI: { 0: null, 7: null },
  };

  // HSI 이미지 데이터 정규화
  const hsiImages = {
    0:
      seq0?.hsi_images_bands?.map((band) => ({
        spectralIndex: band.spectral_index,
        filename: band.filename,
        coordinates: {
          topLeft: band.topLeft,
          topRight: band.topRight,
          bottomRight: band.bottomRight,
          bottomLeft: band.bottomLeft,
        },
      })) ?? [],
    7:
      seq1?.hsi_images_bands?.map((band) => ({
        spectralIndex: band.spectral_index,
        filename: band.filename,
        coordinates: {
          topLeft: band.topLeft,
          topRight: band.topRight,
          bottomRight: band.bottomRight,
          bottomLeft: band.bottomLeft,
        },
      })) ?? [],
  };

  // deepAging: seqnos에 1이 있으면 'Y', 아니면 'N'
  const deepAgingYn =
    Array.isArray(src?.deepAging?.seqnos) && src.deepAging.seqnos.includes(1)
      ? 'Y'
      : 'N';

  return {
    // 상세 표가 item.id를 "이력번호"로 보여오던 흐름을 유지하기 위해 traceNum을 id로 노출
    id: traceId,
    idIndex: idxId, // 내부키 필요 시 사용
    traceNum: traceId,
    status: '대기',

    deepAging: deepAgingYn, // 'Y' | 'N'

    meat: {
      categoryId: src?.meat?.categoryId ?? null, // 부위
      butcheryYmd: src?.meat?.butcheryYmd ?? null, // 도축일자
      birthYmd: src?.meat?.birthYmd ?? null, // 가공일자
      createdAt: src?.meat?.createdAt ?? null, // 업로드/생성일시
      sexType: src?.meat?.sexType ?? null, // 0 암, 1 수
      gradeNum: src?.meat?.gradeNum ?? null, // 등급
    },

    images,
    hsiImages,

    // 분광 곡선 데이터는 현 응답에 없음 → 그래프 섹션에서 "없음"으로 안내
    spectral: { MSI: { 1: null, 7: null }, RGB: { 1: null, 7: null } },

    sensory,
    prediction,

    // 일자별 냉장/숙성 헤더 표기용
    refrigeration: {
      1: !!seq0?.isRefrigerated, // false=냉장, true=숙성
      7: !!seq1?.isRefrigerated,
    },

    // XAI 자산도 보관(향후 사용)
    xai: {
      1: {
        RGB: {
          cam: seq0?.ai_sensory_eval?.xai_imagePath ?? null,
          grade: seq0?.ai_sensory_eval?.xai_gradeNum_imagePath ?? null,
        },
        MSI: {
          cam: seq0?.hsi_sensory_eval?.xai_imagePath ?? null,
          grade: seq0?.hsi_sensory_eval?.xai_gradeNum_imagePath ?? null,
        },
      },
      7: {
        RGB: {
          cam: seq1?.ai_sensory_eval?.xai_imagePath ?? null,
          grade: seq1?.ai_sensory_eval?.xai_gradeNum_imagePath ?? null,
        },
        MSI: {
          cam: seq1?.hsi_sensory_eval?.xai_imagePath ?? null,
          grade: seq1?.hsi_sensory_eval?.xai_gradeNum_imagePath ?? null,
        },
      },
    },
  };
}

export default function MeatDetailPage() {
  const { id } = useParams();
  const nav = useNavigate();
  const location = useLocation();
  const { data, isLoading, isError } = useMeatDetail(id);

  // 상태
  const [mode, setMode] = useState('MSI'); // 'MSI' | 'RGB'
  const [tab, setTab] = useState(0);
  const [selectedWaves, setSelectedWaves] = useState([]);
  const [stateChanged, setStateChanged] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '' });
  const [editMode, setEditMode] = useState(false);
  const [form, setForm] = useState({});
  const [selectedSeqno, setSelectedSeqno] = useState(0); // 선택된 seqno
  const [selectedHsiImageIndex, setSelectedHsiImageIndex] = useState(0); // 선택된 HSI 이미지 인덱스
  const [spectralInfo, setSpectralInfo] = useState([]); // 파장 정보

  // state → 세션 캐시(raw) → null 순으로 복구 + 정규화
  const item = useMemo(() => {
    return data ? normalizeItemFromBackend(data) : null;
  }, [data]);

  // seqno별 탭 생성 (deepAging.seqnos 기반)
  const seqnoTabs = useMemo(() => {
    if (!data?.deepAging?.seqnos) return [];
    return data.deepAging.seqnos.map((seqno) => ({
      seqno,
      label: `가공 ${seqno + 1}회`,
      isRefrigerated:
        data.by_seqno_and_condition?.find((x) => x.seqno === seqno)
          ?.isRefrigerated ?? false,
    }));
  }, [data]);

  // 이번 방문에 state로 넘어왔다면 raw 캐시
  useEffect(() => {
    if (location.state?.item) {
      try {
        sessionStorage.setItem(
          'lastMeatItemRaw',
          JSON.stringify(location.state.item)
        );
      } catch {}
    }
  }, [location.state]);

  // seqno가 변경될 때 HSI 이미지 인덱스 초기화
  useEffect(() => {
    setSelectedHsiImageIndex(0);
  }, [selectedSeqno]);

  // 파장 정보 가져오기
  useEffect(() => {
    const fetchSpectralInfo = async () => {
      try {
        const data = await getSpectralInfo();
        setSpectralInfo(data);
      } catch (error) {
        console.error('Failed to fetch spectral info:', error);
      }
    };
    fetchSpectralInfo();
  }, []);

  function TabPanel({ value, index, children }) {
    return (
      <div role="tabpanel" hidden={value !== index}>
        {value === index && <Box sx={{ mt: 2 }}>{children}</Box>}
      </div>
    );
  }

  // HSI 이미지 슬라이더 컴포넌트
  function HsiImageSlider({
    images,
    title,
    onImageChange,
    selectedIndex,
    spectralInfo,
  }) {
    if (!images || images.length === 0) {
      return (
        <Box sx={{ p: 2, textAlign: 'center', color: 'text.secondary' }}>
          <Typography variant="body2">HSI 이미지가 없습니다</Typography>
        </Box>
      );
    }

    // spectral_index를 실제 파장으로 매핑
    const getWavelength = (spectralIndex) => {
      const info = spectralInfo.find(
        (item) => item.spectral_index === spectralIndex
      );
      return info ? info.wavelength_nm : spectralIndex;
    };

    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="subtitle2" sx={{ mb: 1, color: navy }}>
          {title}
        </Typography>

        {/* 이미지 표시 */}
        <Box
          sx={{
            height: 300,
            border: '1px solid #eee',
            borderRadius: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: '#fafafa',
            mb: 2,
            position: 'relative',
          }}
        >
          {images[selectedIndex] ? (
            <>
              <img
                src={`https://test-deeplant-bucket.s3.ap-northeast-2.amazonaws.com/train_dataset/HSI/${images[selectedIndex].filename}`} // S3 HSI 이미지 경로
                alt={`HSI ${getWavelength(images[selectedIndex].spectralIndex)}nm`}
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
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{
                  display: 'none',
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                }}
              >
                이미지를 불러올 수 없습니다
              </Typography>
            </>
          ) : (
            <Typography variant="body2" color="text.secondary">
              이미지를 불러올 수 없습니다
            </Typography>
          )}
        </Box>

        {/* 파장 선택 슬라이더 */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="caption" sx={{ minWidth: 60 }}>
            파장:
          </Typography>
          <input
            type="range"
            min="0"
            max={Math.max(0, images.length - 1)}
            value={selectedIndex}
            onChange={(e) => onImageChange(parseInt(e.target.value))}
            style={{ flex: 1 }}
          />
          <Typography variant="caption" sx={{ minWidth: 40 }}>
            {getWavelength(images[selectedIndex]?.spectralIndex)}nm
          </Typography>
        </Box>

        {/* 파장별 미리보기 버튼들 */}
        <Box sx={{ display: 'flex', gap: 0.5, mt: 1, flexWrap: 'wrap' }}>
          {images.map((img, idx) => (
            <Button
              key={idx}
              size="small"
              variant={selectedIndex === idx ? 'contained' : 'outlined'}
              onClick={() => onImageChange(idx)}
              sx={{ minWidth: 'auto', px: 1, py: 0.5, fontSize: '0.75rem' }}
            >
              {getWavelength(img.spectralIndex)}nm
            </Button>
          ))}
        </Box>
      </Box>
    );
  }

  // 스펙트럼 안전 접근 (정규화된 구조 전제)
  const getSpectrumSafe = (d) => item?.spectral?.[mode]?.[d] ?? null;

  // 차이가 큰 파장 top-3 자동 선택 (없으면 비움)
  useEffect(() => {
    const spec1 = getSpectrumSafe('1');
    const spec7 = getSpectrumSafe('7');
    if (!spec1 || !spec7) {
      setSelectedWaves([]);
      return;
    }
    const map1 = new Map(spec1.wavelengths.map((w, i) => [w, spec1.values[i]]));
    const map7 = new Map(spec7.wavelengths.map((w, i) => [w, spec7.values[i]]));
    const common = spec1.wavelengths.filter((w) => map7.has(w));
    const diffs = common.map((w) => ({
      w,
      d: Math.abs((map7.get(w) ?? 0) - (map1.get(w) ?? 0)),
    }));
    diffs.sort((a, b) => b.d - a.d);
    setSelectedWaves(diffs.slice(0, 3).map((o) => o.w));
  }, [item, mode]);

  if (!item) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography sx={{ mb: 1 }}>상세 데이터를 찾을 수 없어요.</Typography>
        <Typography variant="body2" color="text.secondary">
          대시보드에서 항목을 클릭해 들어오면 상세 정보가 전달됩니다.
        </Typography>
        <Button sx={{ mt: 2 }} variant="outlined" onClick={() => nav(-1)}>
          뒤로
        </Button>
      </Box>
    );
  }

  const handleReject = async () => {
    try {
      if (!item?.id) return;
      await rejectMeat(item.id, setStateChanged);
      setSnackbar({ open: true, message: '반려되었습니다' });
      setTimeout(() => {
        nav(`/DashBoard?tab`);
      }, 1000);
    } catch (e) {
      console.error('Reject failed:', e);
    }
  };

  const handleConfirm = async () => {
    try {
      if (!item?.id) return;
      await confirmMeat(item.id, setStateChanged);
      setSnackbar({ open: true, message: '승인되었습니다' });
    } catch (e) {
      console.error('Confirm failed:', e);
    }
  };

  const startEdit = () => {
    // 편집 시작 시 현재 상세값을 폼으로 복사
    setForm({
      meatId: item.id, // 현재는 이력번호로 사용 중
      part: item.meat.categoryId ?? '',
      deepAging: item.deepAging ?? '',
      slDate: item.meat.butcheryYmd ?? '',
      processDate: item.meat.birthYmd ?? '',
    });
    setEditMode(true);
  };

  const handleChange = (key, value) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const saveEdit = async () => {
    try {
      if (!form.meatId) return;
      await updateMeatInfo(form);
      setSnackbar({ open: true, message: '수정되었습니다' });
      setEditMode(false);
    } catch (e) {
      console.error('Update failed:', e);
      setSnackbar({ open: true, message: '수정에 실패했습니다' });
      setEditMode(false);
    }
  };

  // 관능/예측 접근 (정규화된 구조 전제)
  const getSensoryByKey = (k) => item?.sensory?.[k] ?? null;
  const getPredictionByKey = (k, m) => item?.prediction?.[k]?.[m] ?? null;

  return (
    <div
      style={{
        overflow: 'auto',
        width: '100%',
        marginTop: 100,
        height: '100%',
        paddingLeft: 30,
        paddingRight: 20,
      }}
    >
      <Snackbar
        open={snackbar.open}
        autoHideDuration={1500}
        onClose={() => setSnackbar({ open: false, message: '' })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        sx={{ bottom: '50% !important' }}
      >
        <Alert severity="success" sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>

      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          minWidth: 634,
        }}
      >
        <span style={{ color: navy, fontSize: 30, fontWeight: 600 }}>
          육류 상세 조회
        </span>
        <ToggleButtonGroup
          size="small"
          value={mode}
          exclusive
          onChange={(_, v) => v && setMode(v)}
        >
          <ToggleButton value="MSI">MSI</ToggleButton>
          <ToggleButton value="RGB">RGB</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mt: 1 }}>
        <Tab label="상세" />
        <Tab label="분석(그래프)" />
      </Tabs>

      {/* seqno별 탭 */}
      {seqnoTabs.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>
            가공 단계별 데이터
          </Typography>
          <Tabs
            value={selectedSeqno}
            onChange={(_, v) => setSelectedSeqno(v)}
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            {seqnoTabs.map(({ seqno, label, isRefrigerated }) => (
              <Tab
                key={seqno}
                value={seqno}
                label={
                  <Box
                    sx={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                    }}
                  >
                    <Typography variant="body2">{label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {isRefrigerated ? '숙성' : '냉장'}
                    </Typography>
                  </Box>
                }
              />
            ))}
          </Tabs>
        </Box>
      )}

      {/* ======================== 상세 탭 ======================== */}
      <TabPanel value={tab} index={0}>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: '1.2fr 1fr',
            gap: 2,
            mt: 3,
          }}
        >
          {/* 좌: HSI 이미지 영역 */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>
              HSI 이미지{' '}
              {`(${selectedSeqno === 0 ? '0일차' : '7일차'} · 파장별 표시)`}
            </Typography>

            {(() => {
              // 선택된 seqno에 해당하는 HSI 이미지 가져오기
              const currentHsiImages =
                item?.hsiImages?.[selectedSeqno === 0 ? '0' : '7'] ?? [];
              const currentSeqnoData = data?.by_seqno_and_condition?.find(
                (x) => x.seqno === selectedSeqno
              );
              const isRefrigerated = currentSeqnoData?.isRefrigerated ?? false;
              const dayLabel = isRefrigerated ? '7일차' : '0일차';
              const conditionLabel = isRefrigerated ? '숙성' : '냉장';

              if (currentHsiImages.length === 0) {
                return (
                  <Box
                    sx={{
                      height: 320,
                      border: '1px solid #eee',
                      borderRadius: 2,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: '#fafafa',
                    }}
                  >
                    <Typography variant="body2" color="text.secondary">
                      {dayLabel} ({conditionLabel}) HSI 이미지가 없습니다
                    </Typography>
                  </Box>
                );
              }

              return (
                <HsiImageSlider
                  images={currentHsiImages}
                  title={`${dayLabel} (${conditionLabel}) HSI 이미지`}
                  selectedIndex={selectedHsiImageIndex}
                  onImageChange={setSelectedHsiImageIndex}
                  spectralInfo={spectralInfo}
                />
              );
            })()}

            {/* QR 영역 */}
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>
              QR 코드
            </Typography>
            <Box
              sx={{
                p: 2,
                border: '1px dashed #ddd',
                display: 'inline-block',
                borderRadius: 2,
              }}
            >
              <Typography variant="caption" color="text.secondary">
                QR 자리 (#{item.id})
              </Typography>
            </Box>
          </Paper>

          {/* 우: 상세정보 표 */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" sx={{ color: navy, mb: 2 }}>
              상세정보
            </Typography>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell width={140} sx={{ color: 'text.secondary' }}>
                    이력번호
                  </TableCell>
                  <TableCell>{item.id}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ color: 'text.secondary' }}>부위</TableCell>
                  <TableCell>
                    {editMode ? (
                      <input
                        value={form.part}
                        onChange={(e) => handleChange('part', e.target.value)}
                        style={{
                          width: '100%',
                          padding: 6,
                          border: '1px solid #ddd',
                          borderRadius: 4,
                        }}
                      />
                    ) : (
                      item.meat.categoryId ?? '-'
                    )}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ color: 'text.secondary' }}>
                    딥에이징 여부
                  </TableCell>
                  <TableCell>
                    {editMode ? (
                      <select
                        value={form.deepAging}
                        onChange={(e) =>
                          handleChange('deepAging', e.target.value)
                        }
                        style={{
                          width: '100%',
                          padding: 6,
                          border: '1px solid #ddd',
                          borderRadius: 4,
                        }}
                      >
                        <option value="">-</option>
                        <option value="Y">Y</option>
                        <option value="N">N</option>
                      </select>
                    ) : (
                      item.deepAging ?? '-'
                    )}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ color: 'text.secondary' }}>
                    도축일자
                  </TableCell>
                  <TableCell>
                    {editMode ? (
                      <input
                        type="date"
                        value={form.slDate}
                        onChange={(e) => handleChange('slDate', e.target.value)}
                        style={{
                          width: '100%',
                          padding: 6,
                          border: '1px solid #ddd',
                          borderRadius: 4,
                        }}
                      />
                    ) : (
                      item.meat.butcheryYmd ?? '-'
                    )}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ color: 'text.secondary' }}>
                    가공일자
                  </TableCell>
                  <TableCell>
                    {editMode ? (
                      <input
                        type="date"
                        value={form.processDate}
                        onChange={(e) =>
                          handleChange('processDate', e.target.value)
                        }
                        style={{
                          width: '100%',
                          padding: 6,
                          border: '1px solid #ddd',
                          borderRadius: 4,
                        }}
                      />
                    ) : (
                      (() => {
                        // 선택된 seqno에 해당하는 가공일자 가져오기
                        const currentSeqnoData =
                          data?.by_seqno_and_condition?.find(
                            (x) => x.seqno === selectedSeqno
                          );
                        const manufactureYmd =
                          currentSeqnoData?.sensory_eval?.manufactureYmd;

                        if (manufactureYmd) {
                          // ISO 날짜 문자열을 YYYY-MM-DD 형식으로 변환
                          const date = new Date(manufactureYmd);
                          return date.toISOString().split('T')[0];
                        }

                        return item.meat.birthYmd ?? '-';
                      })()
                    )}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ color: 'text.secondary' }}>
                    생성일시
                  </TableCell>
                  <TableCell>{item.meat.createdAt ?? '-'}</TableCell>
                </TableRow>
              </TableBody>
            </Table>

            <Divider sx={{ my: 2 }} />
            <Stack direction="row" spacing={1}>
              <Button variant="outlined" color="error" onClick={handleReject}>
                반려
              </Button>
              <Button
                variant="contained"
                color="success"
                onClick={handleConfirm}
              >
                승인
              </Button>
              {editMode ? (
                <Button variant="outlined" onClick={saveEdit}>
                  수정완료
                </Button>
              ) : (
                <Button variant="outlined" onClick={startEdit}>
                  수정
                </Button>
              )}
            </Stack>
          </Paper>
        </Box>

        {/* 하단 비교표 */}
        <Paper sx={{ p: 2, mt: 3 }}>
          <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>
            {selectedSeqno === 0 ? '0일차' : '7일차'} 데이터 비교 (관능 vs{' '}
            {mode})
          </Typography>

          {(() => {
            // 선택된 seqno에 해당하는 데이터 가져오기
            const currentSeqnoData = data?.by_seqno_and_condition?.find(
              (x) => x.seqno === selectedSeqno
            );
            const isRefrigerated = currentSeqnoData?.isRefrigerated ?? false;
            const dayLabel = isRefrigerated ? '7일차' : '0일차';
            const conditionLabel = isRefrigerated ? '숙성' : '냉장';

            const sensory = currentSeqnoData?.sensory_eval;
            const aiPrediction = currentSeqnoData?.ai_sensory_eval;
            const hsiPrediction = currentSeqnoData?.hsi_sensory_eval;
            const aiHsiPrediction = currentSeqnoData?.ai_hsi_sensory_eval;

            const fmt = (v) =>
              v === null || v === undefined || Number.isNaN(v) ? '-' : v;

            return (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>항목</TableCell>
                    <TableCell align="center">관능 평가</TableCell>
                    <TableCell align="center">RGB AI 예측</TableCell>
                    <TableCell align="center">HSI 관능</TableCell>
                    <TableCell align="center">HSI AI 예측</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {LABELS.map(({ key, name }) => {
                    const sensoryVal = sensory?.[key];
                    const aiPredVal = aiPrediction?.[key];
                    const hsiVal = hsiPrediction?.[key];
                    const aiHsiVal = aiHsiPrediction?.[key];

                    return (
                      <TableRow key={key}>
                        <TableCell>{name}</TableCell>
                        <TableCell align="center">{fmt(sensoryVal)}</TableCell>
                        <TableCell align="center">{fmt(aiPredVal)}</TableCell>
                        <TableCell align="center">{fmt(hsiVal)}</TableCell>
                        <TableCell align="center">{fmt(aiHsiVal)}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            );
          })()}
        </Paper>
      </TabPanel>

      {/* ======================== 분석(그래프) 탭 ======================== */}
      <TabPanel value={tab} index={1}>
        {(() => {
          // 선택된 seqno에 해당하는 데이터 가져오기
          const currentSeqnoData = data?.by_seqno_and_condition?.find(
            (x) => x.seqno === selectedSeqno
          );
          const isRefrigerated = currentSeqnoData?.isRefrigerated ?? false;
          const dayLabel = isRefrigerated ? '7일차' : '0일차';
          const conditionLabel = isRefrigerated ? '숙성' : '냉장';

          const sensory = currentSeqnoData?.sensory_eval;
          const aiPrediction = currentSeqnoData?.ai_sensory_eval;
          const hsiPrediction = currentSeqnoData?.hsi_sensory_eval;
          const aiHsiPrediction = currentSeqnoData?.ai_hsi_sensory_eval;

          // (A) 예측값 비교 라인 차트용 데이터
          const predChartData = LABELS.map(({ key, name }) => ({
            항목: name,
            '관능 평가': sensory?.[key] ?? null,
            'RGB AI 예측': aiPrediction?.[key] ?? null,
            'HSI 관능': hsiPrediction?.[key] ?? null,
            'HSI AI 예측': aiHsiPrediction?.[key] ?? null,
          }));

          return (
            <>
              {/* (A) 예측값 라인 차트 */}
              <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>
                  {dayLabel} ({conditionLabel}) 예측값 비교 · {mode}
                </Typography>
                {predChartData.length > 0 ? (
                  <Box sx={{ height: 320 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={predChartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="항목" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="관능 평가"
                          stroke="#8884d8"
                        />
                        <Line
                          type="monotone"
                          dataKey="RGB AI 예측"
                          stroke="#82ca9d"
                        />
                        <Line
                          type="monotone"
                          dataKey="HSI 관능"
                          stroke="#ffc658"
                        />
                        <Line
                          type="monotone"
                          dataKey="HSI AI 예측"
                          stroke="#ff7300"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    예측/관능 데이터가 없습니다.
                  </Typography>
                )}
              </Paper>

              {/* (B) 분광 파장 시계열 - 현재는 데이터 없음 안내 */}
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>
                  분광 파장 시계열 · {mode} · 1일 ↔ 7일 (y=흡수율)
                </Typography>

                {(() => {
                  const spec1 = getSpectrumSafe('1');
                  const spec7 = getSpectrumSafe('7');

                  if (!spec1 || !spec7) {
                    return (
                      <Typography variant="body2" color="text.secondary">
                        분광 데이터가 없습니다.{' '}
                        <code>
                          spectral.{'{MSI|RGB}'}.{'{1|7}'}
                        </code>{' '}
                        형태의 데이터를 제공하면 파장-흡수율 그래프가
                        표시됩니다.
                      </Typography>
                    );
                  }

                  // 공통 파장 풀
                  const map1 = new Map(
                    spec1.wavelengths.map((w, i) => [w, spec1.values[i]])
                  );
                  const map7 = new Map(
                    spec7.wavelengths.map((w, i) => [w, spec7.values[i]])
                  );
                  const availableWaves = spec1.wavelengths.filter((w) =>
                    map7.has(w)
                  );

                  // 선택된 파장들(최대 5개)
                  const chosen = (selectedWaves || [])
                    .filter((w) => availableWaves.includes(w))
                    .slice(0, 5);
                  const keyLabel = (w) => `${w}nm`;

                  // 시간축 시리즈 (1일/7일)
                  const timeSeries = [
                    Object.fromEntries([
                      ['day', '1일'],
                      ...chosen.map((w) => [keyLabel(w), map1.get(w)]),
                    ]),
                    Object.fromEntries([
                      ['day', '7일'],
                      ...chosen.map((w) => [keyLabel(w), map7.get(w)]),
                    ]),
                  ];

                  return (
                    <>
                      {/* 파장 선택 UI */}
                      <FormControl size="small" sx={{ minWidth: 260, mb: 1 }}>
                        <InputLabel>파장 선택</InputLabel>
                        <Select
                          multiple
                          value={chosen.length ? chosen : []}
                          onChange={(e) => {
                            const val =
                              typeof e.target.value === 'string'
                                ? e.target.value.split(',')
                                : e.target.value;
                            setSelectedWaves(val.map((v) => Number(v)));
                          }}
                          input={<OutlinedInput label="파장 선택" />}
                          renderValue={(sel) =>
                            sel.map((w) => `${w}nm`).join(', ')
                          }
                        >
                          {availableWaves.map((w) => (
                            <MenuItem key={w} value={w}>
                              <Checkbox
                                checked={(selectedWaves || []).indexOf(w) > -1}
                              />
                              <ListItemText primary={`${w} nm`} />
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>

                      {/* 라인 차트 */}
                      <Box sx={{ height: 320 }}>
                        {chosen.length ? (
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={timeSeries}>
                              <CartesianGrid strokeDasharray="3 3" />
                              <XAxis dataKey="day" />
                              <YAxis
                                label={{
                                  value: '흡수율',
                                  angle: -90,
                                  position: 'insideLeft',
                                }}
                                domain={['auto', 'auto']}
                              />
                              <Tooltip />
                              <Legend />
                              {chosen.map((w) => (
                                <Line
                                  key={w}
                                  type="monotone"
                                  dataKey={keyLabel(w)}
                                />
                              ))}
                            </LineChart>
                          </ResponsiveContainer>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
                            비교할 파장을 선택하세요.
                          </Typography>
                        )}
                      </Box>
                    </>
                  );
                })()}
              </Paper>
            </>
          );
        })()}
      </TabPanel>
    </div>
  );
}
