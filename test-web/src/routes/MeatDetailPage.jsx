// src/routes/MeatDetailPage.jsx
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import {
  Box, Paper, Typography, Chip, Divider, Button,
  Table, TableHead, TableRow, TableCell, TableBody, Stack
} from '@mui/material';
import { useState, useMemo } from 'react';
import { ToggleButton, ToggleButtonGroup } from '@mui/material';

const navy = '#0F3659';

export default function MeatDetailPage() {
  const { id } = useParams();
  const nav = useNavigate();
  const location = useLocation();

  // 1) 대시보드에서 넘긴 state


  // 2) 혹시 새로고침했거나 직접 URL 접근 시: 직전에 본 항목 복구 시도


  const item = location.state?.item
  //msi,rgb | day 전환용 상태값
  const [mode, setMode] = useState('MSI'); // 'MSI" | "RGB"
  const [day, setDay] = useState('0'); // 0 | 7
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
    ['가공일자', item.ProcessDate],
    ['업로드 일시', item.timestamp],
  ];

  const labels = [
    '색상(Color)', '향(Aroma)', '조직감(Texture)',
    '즙성(Juiciness)', '풍미(Flavor)', '전체 기호도'
  ];

  return (
    <div style={{ overflow: 'auto', width: '100%', marginTop: 100, height: '100%', paddingLeft: 30, paddingRight: 20 }}>
      <Box sx={{ display:'flex', justifyContent:'space-between', alignItems:'center', minWidth: 634 }}>
        <span style={{ color: navy, fontSize: 30, fontWeight: 600 }}>육류 상세 조회</span>
        <Chip label={item.status || '대기'} color={statusColor} />
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
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
              {infoRows.map(([k, v]) => (
                <TableRow key={k}>
                  <TableCell width={140} sx={{ color: 'text.secondary' }}>{k}</TableCell>
                  <TableCell>{v ?? '-'}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <Divider sx={{ my: 2 }} />
          <Stack direction="row" spacing={1}>
            <Button variant="outlined" color="error">반려</Button>
            <Button variant="contained" color="success">승인</Button>
            <Button variant="outlined">수정</Button>
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

    </div>
  );
}
