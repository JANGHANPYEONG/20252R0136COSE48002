// src/routes/MeatDetailPage.jsx
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import {
  Box, Paper, Typography, Chip, Divider, Button,
  Table, TableHead, TableRow, TableCell, TableBody, Stack,
  Snackbar, Alert
} from '@mui/material';
import { useEffect, useState, useMemo } from 'react';
import { Tabs, Tab, ToggleButton, ToggleButtonGroup } from '@mui/material';
// MUI - 멀티셀렉트 UI
import {
  FormControl, InputLabel, Select, MenuItem, Checkbox, ListItemText, OutlinedInput
} from '@mui/material';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from 'recharts';
import { updateDataStatus } from '../API/updateDataStatus';
import { updateMeatInfo } from '../API/add/updateMeatInfo';
const navy = '#0F3659';

export default function MeatDetailPage() {
  const { id } = useParams();
  const nav = useNavigate();
  const location = useLocation();

  // 상태 및 헬퍼 추가
  // 상태 및 헬퍼 추가  (⚠️ item, mode를 가장 먼저 준비)
  const [mode, setMode] = useState('MSI');  // 'MSI' | 'RGB'
  const [tab, setTab] = useState(0);
  const [selectedWaves, setSelectedWaves] = useState([]);
  const [stateChanged, setStateChanged] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '' });
  const [editMode, setEditMode] = useState(false);
  const [form, setForm] = useState({});

  // state → 세션 캐시 → null 순으로 복구
  const item = useMemo(() => {
    if (location.state?.item) return location.state.item;
    try {
      const cached = sessionStorage.getItem('lastMeatItem');
      return cached ? JSON.parse(cached) : null;
    } catch {
      return null;
    }
  }, [location.state]);

  // 이번 방문에 state로 넘어왔다면 캐시
  useEffect(() => {
    if (location.state?.item) {
      try { sessionStorage.setItem('lastMeatItem', JSON.stringify(location.state.item)); } catch {}
    }
  }, [location.state]);

  function TabPanel({ value, index, children }) {
    return (
      <div role="tabpanel" hidden={value !== index}>
        {value === index && <Box sx={{ mt: 2 }}>{children}</Box>}
      </div>
    );
  }

  // 스펙트럼 안전 접근 헬퍼 (⚠️ item/mode 선언 이후에 정의)
  const getSpectrumSafe = (d) => {
    const specRoot = item?.spectral || item?.spectrum;
    const obj =
      specRoot?.[mode]?.[d] ||
      specRoot?.[mode?.toLowerCase?.()]?.[d] ||
      item?.[`${mode}_spectrum_${d}`] ||
      item?.[`${mode?.toLowerCase?.()}_spectrum_${d}`] ||
      item?.[`${mode}_spec_${d}`] ||
      item?.[`${mode?.toLowerCase?.()}_spec_${d}`];

    if (!obj) return null;
    const wavelengths = obj.wavelengths || obj.w || obj.lambda;
    const values = obj.values || obj.v || obj.intensity;
    if (!Array.isArray(wavelengths) || !Array.isArray(values)) return null;
    return { wavelengths, values };
  };

  // 차이가 큰 파장 top-3 자동 선택 (item 없으면 스킵)
  useEffect(() => {
    if (!item) { setSelectedWaves([]); return; }

    const spec1 = getSpectrumSafe('1') || getSpectrumSafe('0');
    const spec7 = getSpectrumSafe('7');
    if (!spec1 || !spec7) { setSelectedWaves([]); return; }

    const map1 = new Map(spec1.wavelengths.map((w, i) => [w, spec1.values[i]]));
    const map7 = new Map(spec7.wavelengths.map((w, i) => [w, spec7.values[i]]));
    const common = spec1.wavelengths.filter((w) => map7.has(w));
    const diffs = common.map((w) => ({ w, d: Math.abs((map7.get(w) ?? 0) - (map1.get(w) ?? 0)) }));
    diffs.sort((a, b) => b.d - a.d);
    setSelectedWaves(diffs.slice(0, 3).map(o => o.w));
  }, [item, mode]);

  // ❌ 더 이상 day 상태는 쓰지 않으므로 제거
  // const [day, setDay] = useState('0');

  if (!item) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography sx={{ mb: 1 }}>상세 데이터를 찾을 수 없어요.</Typography>
        <Typography variant="body2" color="text.secondary">
          대시보드에서 항목을 클릭해 들어오면 상세 정보가 전달됩니다.
        </Typography>
        <Button sx={{ mt: 2 }} variant="outlined" onClick={() => nav(-1)}>뒤로</Button>
      </Box>
    );
  }

  const statusColor =
    item.status === '승인' ? 'success' : item.status === '반려' ? 'error' : 'default';

  const infoRows = [
    ['이력번호', item.id],
    ['샘플번호', item.sampleNo],
    ['부위', item.part],
    ['딥에이징 여부', item.deepAging],
    ['도축일자', item.slDate],
    ['가공일자', item.processDate],
    ['업로드 일시', item.timestamp],
  ];

  const labels = [
    '색상(Color)', '향(Aroma)', '조직감(Texture)',
    '즙성(Juiciness)', '풍미(Flavor)', '전체 기호도'
  ];

  const handleReject = async () => {
    try {
      if (!item?.id) return;
      await updateDataStatus('reject', item.id, setStateChanged);
      // 안내 후 대시보드 탭으로 이동
      setSnackbar({ open: true, message: '반려되었습니다' });
      setTimeout(() => {
        nav(`/NewDashboard?tab`);
      }, 1000);
    } catch (e) {
      // 실패해도 콘솔만 남기고 현재 페이지 유지
      // 실제 운영 시 사용자 알림 토스트 등 추가 권장
      // eslint-disable-next-line no-console
      console.error('Reject failed:', e);
    }
  };

  const handleConfirm = async () => {
    try {
      if (!item?.id) return;
      await updateDataStatus('confirm', item.id, setStateChanged);
      setSnackbar({ open: true, message: '승인되었습니다' });
    } catch (e) {
      console.error('Confirm failed:', e);
    }
  };

  const startEdit = () => {
    // 편집 시작 시 현재 상세값을 폼으로 복사
    setForm({
      meatId: item.id,
      sampleNo: item.sampleNo ?? '',
      part: item.part ?? '',
      deepAging: item.deepAging ?? '',
      slDate: item.slDate ?? '',
      processDate: item.processDate ?? '',
    });
    setEditMode(true);
  };

  const handleChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const saveEdit = async () => {
    try {
      if (!form.meatId) return;
      await updateMeatInfo(form);
      setSnackbar({ open: true, message: '수정되었습니다' });
      setEditMode(false);
    } catch (e) {
      // eslint-disable-next-line no-console
      console.error('Update failed:', e);
      setSnackbar({ open: true, message: '수정에 실패했습니다' });
      setEditMode(false);
    }
  };


  return (
    <div style={{ overflow: 'auto', width: '100%', marginTop: 100, height: '100%', paddingLeft: 30, paddingRight: 20 }}>
      <Snackbar
        open={snackbar.open}
        autoHideDuration={1500}
        onClose={() => setSnackbar({ open: false, message: '' })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        sx={{ bottom: '50% !important'}}
      >
        <Alert severity="success" sx={{ width: '100%'}}>
          {snackbar.message}
        </Alert>
      </Snackbar>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', minWidth: 634 }}>
        <span style={{ color: navy, fontSize: 30, fontWeight: 600 }}>육류 상세 조회</span>
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

      <TabPanel value={tab} index={0}>
        <Box sx={{ display:'grid', gridTemplateColumns:'1.2fr 1fr', gap: 2, mt: 3 }}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>
            육류 이미지 {`(${mode} · 0/7일차 동시 표시)`}
          </Typography>

          {(() => {
            // 이미지 소스 탐색 (여러 형태 폴백)
            const getImg = (d) =>
              item?.images?.[mode]?.[d] ||
              item?.image?.[mode]?.[d] ||
              item?.[`image_${mode}_${d}`] ||
              item?.[`${mode.toLowerCase()}Image_${d}`] ||
              item?.[`${mode.toLowerCase()}_image_${d}`];

            const renderDayBox = (dLabel) => {
              const src = getImg(dLabel);
              return (
                <Box
                  key={dLabel}
                  sx={{
                    position: 'relative',
                    border: '1px solid #eee',
                    borderRadius: 2,
                    p: 1,
                    height: 320,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: '#fafafa',
                  }}
                >
                  {/* 좌상단 배지 */}
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 8,
                      left: 8,
                      px: 1,
                      py: 0.25,
                      fontSize: 12,
                      borderRadius: 1,
                      bgcolor: '#e7f1ff',
                      color: navy,
                      border: '1px solid #cfe3ff',
                    }}
                  >
                    {dLabel}일차
                  </Box>

                  {src ? (
                    <img
                      src={src}
                      alt={`${item.id} ${mode} ${dLabel}일차`}
                      style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', borderRadius: 8 }}
                    />
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      ({mode} · {dLabel}일차 이미지가 없습니다)
                    </Typography>
                  )}
                </Box>
              );
            };

            return (
              <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mb: 2 }}>
                {renderDayBox('0')}
                {renderDayBox('7')}
              </Box>
            );
          })()}

          {/* 이하 QR 영역은 그대로 */}
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>QR 코드</Typography>
          <Box sx={{ p: 2, border: '1px dashed #ddd', display: 'inline-block', borderRadius: 2 }}>
            <Typography variant="caption" color="text.secondary">QR 자리 (#{item.id})</Typography>
          </Box>
        </Paper>

          {/* 우: 상세정보 표 */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" sx={{ color: navy, mb: 2 }}>상세정보</Typography>
            <Table size="small">
              <TableBody>
                <TableRow>
                  <TableCell width={140} sx={{ color: 'text.secondary' }}>이력번호</TableCell>
                  <TableCell>{item.id}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ color: 'text.secondary' }}>샘플번호</TableCell>
                  <TableCell>
                    {editMode ? (
                      <input
                        value={form.sampleNo}
                        onChange={(e) => handleChange('sampleNo', e.target.value)}
                        style={{ width: '100%', padding: 6, border: '1px solid #ddd', borderRadius: 4 }}
                      />
                    ) : (item.sampleNo ?? '-')}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ color: 'text.secondary' }}>부위</TableCell>
                  <TableCell>
                    {editMode ? (
                      <input
                        value={form.part}
                        onChange={(e) => handleChange('part', e.target.value)}
                        style={{ width: '100%', padding: 6, border: '1px solid #ddd', borderRadius: 4 }}
                      />
                    ) : (item.part ?? '-')}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ color: 'text.secondary' }}>딥에이징 여부</TableCell>
                  <TableCell>
                    {editMode ? (
                      <select
                        value={form.deepAging}
                        onChange={(e) => handleChange('deepAging', e.target.value)}
                        style={{ width: '100%', padding: 6, border: '1px solid #ddd', borderRadius: 4 }}
                      >
                        <option value="">-</option>
                        <option value="Y">Y</option>
                        <option value="N">N</option>
                      </select>
                    ) : (item.deepAging ?? '-')}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ color: 'text.secondary' }}>도축일자</TableCell>
                  <TableCell>
                    {editMode ? (
                      <input
                        type="date"
                        value={form.slDate}
                        onChange={(e) => handleChange('slDate', e.target.value)}
                        style={{ width: '100%', padding: 6, border: '1px solid #ddd', borderRadius: 4 }}
                      />
                    ) : (item.slDate ?? '-')}
                  </TableCell>
                </TableRow>
                <TableRow>
                  <TableCell sx={{ color: 'text.secondary' }}>가공일자</TableCell>
                  <TableCell>
                    {editMode ? (
                      <input
                        type="date"
                        value={form.processDate}
                        onChange={(e) => handleChange('processDate', e.target.value)}
                        style={{ width: '100%', padding: 6, border: '1px solid #ddd', borderRadius: 4 }}
                      />
                    ) : (item.processDate ?? '-')}
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>

            <Divider sx={{ my: 2 }} />
            <Stack direction="row" spacing={1}>
              <Button variant="outlined" color="error" onClick={handleReject}>반려</Button>
              <Button variant="contained" color="success" onClick={handleConfirm}>승인</Button>
              {editMode ? (
                <Button variant="outlined" onClick={saveEdit}>수정완료</Button>
              ) : (
                <Button variant="outlined" onClick={startEdit}>수정</Button>
              )}
            </Stack>
          </Paper>
        </Box>

        {/* 하단 비교표 */}
        <Paper sx={{ p: 2, mt: 3 }}>
          <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>
            1일차 · 7일차 비교 (관능 vs { (typeof mode !== 'undefined' && mode) ? mode : 'MSI' })
          </Typography>

          {(() => {
            // ===== helpers =====
            const MODE = (typeof mode !== 'undefined' && mode) ? mode : 'MSI'; // 토글 없으면 MSI 고정
            const getSensoryByKey = (k) =>
              item?.[`sensory${k}`] ||
              item?.sensory?.[k] ||
              item?.sensory?.[`day${k}`] ||
              (k === '1' ? (item?.sensory1 || item?.sensory0 || item?.sensory) : undefined) ||
              (k === '7' ? (item?.sensory7 || item?.sensory?.['7'] || item?.sensory?.day7) : undefined);

            const getPredictionByKey = (k) => {
              const pred = item?.prediction || item?.predictions;
              if (!pred) return undefined;

              // 지원: prediction['1'|'7']?.[MODE], prediction.day1?.MSI, prediction.MSI_1 등
              const dayObj =
                pred?.[k] ||
                pred?.[`day${k}`] ||
                pred?.[`D${k}`];

              const byNested =
                dayObj?.[MODE] ||
                dayObj?.[MODE.toLowerCase()];

              const byFlat =
                pred?.[`${MODE}_${k}`] ||
                pred?.[`${MODE.toLowerCase()}_${k}`];

              return byNested || byFlat;
            };

            // 1일차: 없으면 0일차로 폴백
            const s1 = getSensoryByKey('1') || getSensoryByKey('0');
            const p1 = getPredictionByKey('1') || getPredictionByKey('0');

            // 7일차
            const s7 = getSensoryByKey('7');
            const p7 = getPredictionByKey('7');

            const getVal = (obj, key) => (obj ? obj[key] : undefined);
            const fmt = (v) => (v === null || v === undefined || Number.isNaN(v) ? '-' : v);
            const diffNum = (a, b) =>
              (typeof a === 'number' && typeof b === 'number') ? (a - b).toFixed(2) : '-';

            return (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell rowSpan={2}>항목</TableCell>
                    <TableCell align="center" colSpan={2}>{item?.deepAging === 'Y' ? '숙성' : '냉장'} 1일차</TableCell>
                    <TableCell align="center" colSpan={2}>{item?.deepAging === 'Y' ? '숙성' : '냉장'} 7일차</TableCell>
                    <TableCell align="center" colSpan={1}>예측값 비교</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>관능</TableCell>
                    <TableCell>{MODE} 예측</TableCell>

                    <TableCell>관능</TableCell>
                    <TableCell>{MODE} 예측</TableCell>

                    <TableCell>예측 차이(7일−1일)</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {labels.map((label) => {
                    const s1v = getVal(s1, label);
                    const p1v = getVal(p1, label);

                    const s7v = getVal(s7, label);
                    const p7v = getVal(p7, label);

                    const predGap = diffNum(p7v, p1v);

                    return (
                      <TableRow key={label}>
                        <TableCell>{label}</TableCell>

                        {/* 1일차 */}
                        <TableCell>{fmt(s1v)}</TableCell>
                        <TableCell>{fmt(p1v)}</TableCell>

                        {/* 7일차 */}
                        <TableCell>{fmt(s7v)}</TableCell>
                        <TableCell>{fmt(p7v)}</TableCell>

                        {/* 비교 */}
                        <TableCell>{predGap}</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            );
          })()}
        </Paper>
      </TabPanel>
      <TabPanel value={tab} index={1}>
        {/* ===== 데이터 헬퍼들 ===== */}
        {(() => {
          // 관능/예측 접근
          const getSensoryByKey = (k) =>
            item?.[`sensory${k}`] ||
            item?.sensory?.[k] ||
            item?.sensory?.[`day${k}`] ||
            (k === '1' ? (item?.sensory1 || item?.sensory0 || item?.sensory) : undefined) ||
            (k === '7' ? (item?.sensory7 || item?.sensory?.['7'] || item?.sensory?.day7) : undefined);

          const getPredictionByKey = (k, m) => {
            const pred = item?.prediction || item?.predictions;
            if (!pred) return undefined;
            const dayObj = pred?.[k] || pred?.[`day${k}`] || pred?.[`D${k}`];
            const byNested = dayObj?.[m] || dayObj?.[m.toLowerCase()];
            const byFlat = pred?.[`${m}_${k}`] || pred?.[`${m.toLowerCase()}_${k}`];
            return byNested || byFlat;
          };

          // 분광 데이터 접근 (여러 형태 폴백)
          const getSpectrum = (d, m) => {
            // 기대 형태:
            // item.spectral?.[m]?.[d] = { wavelengths: [...], values: [...] }
            // 또는 item.spectrum?.[m]?.[d], item[`${m}_spectrum_${d}`] 등
            const specRoot = item?.spectral || item?.spectrum;
            const byNested = specRoot?.[m]?.[d] || specRoot?.[m.toLowerCase()]?.[d];
            const byFlat =
              item?.[`${m}_spectrum_${d}`] || item?.[`${m.toLowerCase()}_spectrum_${d}`] ||
              item?.[`${m}_spec_${d}`] || item?.[`${m.toLowerCase()}_spec_${d}`];

            const obj = byNested || byFlat;
            if (!obj) return undefined;

            const wavelengths = obj.wavelengths || obj.w || obj.lambda;
            const values = obj.values || obj.v || obj.intensity;
            if (!Array.isArray(wavelengths) || !Array.isArray(values)) return undefined;

            return { wavelengths, values };
          };

          const s1 = getSensoryByKey('1') || getSensoryByKey('0'); // 1일차 없으면 0일차 폴백
          const s7 = getSensoryByKey('7');
          const p1 = getPredictionByKey('1', mode) || getPredictionByKey('0', mode);
          const p7 = getPredictionByKey('7', mode);

          // ----- (A) 예측값 비교 차트용 데이터 (카테고리: labels) -----
          const predChartData = (labels || []).map((lab) => ({
            항목: lab,
            '관능 1일': s1?.[lab] ?? null,
            [`${mode} 예측 1일`]: p1?.[lab] ?? null,
            '관능 7일': s7?.[lab] ?? null,
            [`${mode} 예측 7일`]: p7?.[lab] ?? null,
          }));

          // ----- (B) 분광 파장 시계열 (x: nm, y: intensity) -----
          const spec0 = getSpectrum('0', mode) || getSpectrum('1', mode); // 0 없으면 1
          const spec7 = getSpectrum('7', mode);

          let spectralSeries = [];
          if (spec0?.wavelengths && spec0?.values && spec7?.wavelengths && spec7?.values) {
            const L = Math.min(spec0.wavelengths.length, spec0.values.length, spec7.wavelengths.length, spec7.values.length);
            spectralSeries = Array.from({ length: L }).map((_, i) => ({
              nm: spec0.wavelengths[i] ?? spec7.wavelengths[i],
              '0일(또는1일)': spec0.values[i],
              '7일': spec7.values[i],
            }));
          }

          return (
            <>
              {/* (A) 예측값 라인 차트 */}
              <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>
                  예측값 비교 (1일 vs 7일) · {mode}
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
                        <Line type="monotone" dataKey="관능 1일" />
                        <Line type="monotone" dataKey={`${mode} 예측 1일`} />
                        <Line type="monotone" dataKey="관능 7일" />
                        <Line type="monotone" dataKey={`${mode} 예측 7일`} />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">예측/관능 데이터가 없습니다.</Typography>
                )}
              </Paper>
              {/* (B) 분광 파장 시계열 - x축: 시계열(1일/7일), y축: 흡수율 */}
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>
                  분광 파장 시계열 · {mode} · 1일 ↔ 7일 (y=흡수율)
                </Typography>

                {(() => {
                  const spec1 = getSpectrumSafe('1') || getSpectrumSafe('0'); // 1일 없으면 0일 폴백
                  const spec7 = getSpectrumSafe('7');

                  if (!spec1 || !spec7) {
                    return (
                      <Typography variant="body2" color="text.secondary">
                        분광 데이터가 없습니다. <code>spectral.{'{MSI|RGB}'}.{'{1|7}'}</code> 또는 <code>0</code> 형태를 제공하세요.
                      </Typography>
                    );
                  }

                  // 공통 파장 풀
                  const map1 = new Map(spec1.wavelengths.map((w, i) => [w, spec1.values[i]]));
                  const map7 = new Map(spec7.wavelengths.map((w, i) => [w, spec7.values[i]]));
                  const availableWaves = spec1.wavelengths.filter((w) => map7.has(w));

                  // 선택된 파장들만 최대 5개 사용
                  const chosen = (selectedWaves || []).filter((w) => availableWaves.includes(w)).slice(0, 5);
                  const keyLabel = (w) => `${w}nm`;

                  // 차트 데이터: x축=시계열(1일/7일), 각 파장별 y=흡수율
                  const timeSeries = [
                    Object.fromEntries([['day', '1일'], ...chosen.map((w) => [keyLabel(w), map1.get(w)])]),
                    Object.fromEntries([['day', '7일'], ...chosen.map((w) => [keyLabel(w), map7.get(w)])]),
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
                            const val = typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value;
                            setSelectedWaves(val.map((v) => Number(v)));
                          }}
                          input={<OutlinedInput label="파장 선택" />}
                          renderValue={(sel) => sel.map((w) => `${w}nm`).join(', ')}
                        >
                          {availableWaves.map((w) => (
                            <MenuItem key={w} value={w}>
                              <Checkbox checked={(selectedWaves || []).indexOf(w) > -1} />
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
                                label={{ value: '흡수율', angle: -90, position: 'insideLeft' }}
                                domain={['auto', 'auto']}
                              />
                              <Tooltip />
                              <Legend />
                              {chosen.map((w) => (
                                <Line key={w} type="monotone" dataKey={keyLabel(w)} />
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
