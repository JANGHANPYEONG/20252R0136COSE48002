// src/routes/MeatDetailPage.jsx
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import {
  Box, Paper, Typography, Chip, Divider, Button,
  Table, TableHead, TableRow, TableCell, TableBody, Stack
} from '@mui/material';
import { useMemo } from 'react';

const navy = '#0F3659';

export default function MeatDetailPage() {
  const { id } = useParams();
  const nav = useNavigate();
  const location = useLocation();

  // 1) 대시보드에서 넘긴 state


  // 2) 혹시 새로고침했거나 직접 URL 접근 시: 직전에 본 항목 복구 시도


  const item = location.state?.item

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
    ['딥에이징 여부', item.deepAging ? 'Y' : 'N'],
    ['도축일자', item.slDate],
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

      <Box sx={{ display:'grid', gridTemplateColumns:'1.2fr 1fr', gap: 2, mt: 3 }}>
        {/* 좌: 이미지/QR */}
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>육류 이미지</Typography>
          <Box sx={{ border:'1px solid #eee', borderRadius: 2, p: 1, height: 320, display:'flex', alignItems:'center', justifyContent:'center', bgcolor:'#fafafa' }}>
            <Typography variant="body2" color="text.secondary">
              (사진이 들어갈 예정입니다)
            </Typography>
          </Box>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>QR 코드</Typography>
          <Box sx={{ p: 2, border:'1px dashed #ddd', display:'inline-block', borderRadius: 2 }}>
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
          관능평가 vs 예측 결과 비교
        </Typography>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>항목</TableCell>
              <TableCell>관능(Sensory)</TableCell>
              <TableCell>예측(Prediction)</TableCell>
              <TableCell>차이(예측-관능)</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {labels.map((label) => {
              const s = item.sensory?.[label];
              const p = item.prediction?.[label];
              const diff = (p ?? null) !== null && (s ?? null) !== null ? (p - s).toFixed(2) : '-';
              return (
                <TableRow key={label}>
                  <TableCell>{label}</TableCell>
                  <TableCell>{s ?? '-'}</TableCell>
                  <TableCell>{p ?? '-'}</TableCell>
                  <TableCell>{diff}</TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Paper>
    </div>
  );
}
