// src/routes/SpectralSender.jsx
import { useState, useMemo } from 'react';
import {
  Box, Button, Chip, TextField, Typography, Paper, Stack, Snackbar, Alert
} from '@mui/material';
import { submitSpectrals } from '../API/spectrals/submitSpectrals';

const navy = '#0F3659';

export default function SpectralSender() {
  const [input, setInput] = useState('');           // 단일 입력창
  const [bulk, setBulk]   = useState('');           // 여러 개 붙여넣기
  const [values, setValues] = useState([]);         // 최종 파장 리스트 (정수 nm)
  const [endpoint, setEndpoint] = useState('/spectral/spectral-info/bulk'); // 필요 시 수정
  const [snack, setSnack] = useState({ open: false, severity: 'info', message: '' });
  const [posting, setPosting] = useState(false);

  // JSON 미리보기
  const preview = useMemo(() => ({
    spectrals: values.map((wl, i) => ({ spectral_index: i, wavelength_nm: wl })),
  }), [values]);

  const addValue = () => {
    const n = Number.parseInt(input.trim(), 10);
    if (Number.isNaN(n)) {
      setSnack({ open: true, severity: 'warning', message: '정수 nm로 입력해주세요 (예: 430)' });
      return;
    }
    if (n < 300 || n > 1100) {
      setSnack({ open: true, severity: 'warning', message: '300~1100 nm 범위로 입력해주세요' });
      return;
    }
    if (values.includes(n)) {
      setSnack({ open: true, severity: 'info', message: '이미 추가된 파장입니다' });
      return;
    }
    setValues((prev) => [...prev, n]);
    setInput('');
  };

  const removeValue = (wl) => {
    setValues((prev) => prev.filter((x) => x !== wl));
  };

  const parseBulk = () => {
    // 쉼표, 공백, 줄바꿈으로 구분된 여러 값 처리
    const tokens = bulk.split(/[\s,]+/).filter(Boolean);
    if (tokens.length === 0) {
      setSnack({ open: true, severity: 'info', message: '추가할 값이 없습니다' });
      return;
    }
    let added = 0;
    const next = [...values];
    const seen = new Set(next);
    tokens.forEach((t) => {
      const n = Number.parseInt(t.trim(), 10);
      if (!Number.isNaN(n) && n >= 300 && n <= 1100 && !seen.has(n)) {
        next.push(n);
        seen.add(n);
        added += 1;
      }
    });
    setValues(next);
    setSnack({
      open: true,
      severity: added > 0 ? 'success' : 'info',
      message: added > 0 ? `${added}개 추가됨` : '추가할 유효 값이 없습니다',
    });
  };

  const clearAll = () => {
    setValues([]);
    setInput('');
    setBulk('');
  };

  const postNow = async () => {
    if (values.length === 0) {
      setSnack({ open: true, severity: 'warning', message: '먼저 파장을 하나 이상 추가하세요' });
      return;
    }
    try {
      setPosting(true);
      const json = await submitSpectrals(values, endpoint);
      setSnack({ open: true, severity: 'success', message: '전송 완료!' });
      // 필요 시 응답 처리 로직 추가
      // console.log('서버 응답:', json);
    } catch (e) {
      setSnack({ open: true, severity: 'error', message: `전송 실패: ${e.message}` });
    } finally {
      setPosting(false);
    }
  };

  return (
    <div style={{ overflow: 'auto', width: '100%', marginTop: '100px', height: '100%', paddingLeft: '30px', paddingRight: '20px' }}>
      {/* 페이지 타이틀 */}
      <Box style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', minWidth: '634px' }}>
        <span style={{ color: navy, fontSize: '30px', fontWeight: 600 }}>Spectral Selector</span>
      </Box>

      <Box sx={{ mt: 3, display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: 2 }}>
        {/* 좌측: 입력 영역 */}
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" sx={{ color: navy, mb: 2 }}>파장 입력 (nm)</Typography>

          <Stack direction="row" spacing={1} alignItems="center">
            <TextField
              size="small"
              label="정수 nm (예: 430)"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') addValue(); }}
            />
            <Button variant="contained" onClick={addValue} sx={{ bgcolor: navy, '&:hover': { bgcolor: '#0a2a4a' } }}>
              추가
            </Button>
            <Button variant="outlined" color="inherit" onClick={clearAll}>
              초기화
            </Button>
          </Stack>

          <Typography variant="body2" sx={{ mt: 2, color: 'text.secondary' }}>
            여러 개를 한 번에 추가하려면 아래에 쉼표/스페이스/줄바꿈으로 구분하여 붙여넣기 후 “한꺼번에 추가”.
          </Typography>

          <Stack spacing={1} sx={{ mt: 1 }}>
            <TextField
              multiline
              minRows={3}
              placeholder={`예)\n430, 450 470\n490`}
              value={bulk}
              onChange={(e) => setBulk(e.target.value)}
            />
            <Button variant="outlined" onClick={parseBulk}>한꺼번에 추가</Button>
          </Stack>

          <Typography variant="subtitle2" sx={{ mt: 2, color: navy }}>추가된 파장</Typography>
          <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {values.map((wl) => (
              <Chip key={wl} label={`${wl} nm`} onDelete={() => removeValue(wl)} />
            ))}
            {values.length === 0 && (
              <Typography variant="body2" color="text.secondary">아직 없음</Typography>
            )}
          </Box>
        </Paper>

        {/* 우측: 미리보기 & 전송 */}
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" sx={{ color: navy, mb: 1 }}>전송 JSON 미리보기</Typography>
          <Box
            component="pre"
            sx={{
              m: 0, p: 1.5, border: '1px solid #eee', borderRadius: 1,
              bgcolor: '#fafafa', fontSize: 13, maxHeight: 240, overflow: 'auto'
            }}
          >
            {JSON.stringify(preview, null, 2)}
          </Box>

          <TextField
            label="POST Endpoint"
            size="small"
            sx={{ mt: 2 }}
            value={endpoint}
            onChange={(e) => setEndpoint(e.target.value)}
            helperText="기본값: /hsi/spectrals (백엔드 경로에 맞춰 변경)"
          />

          <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
            <Button
              variant="contained"
              onClick={postNow}
              disabled={posting || values.length === 0}
              sx={{ bgcolor: navy, '&:hover': { bgcolor: '#0a2a4a' } }}
            >
              {posting ? '전송 중…' : '전송'}
            </Button>
            <Button variant="outlined" onClick={clearAll}>초기화</Button>
          </Stack>
        </Paper>
      </Box>

      <Snackbar
        open={snack.open}
        autoHideDuration={3500}
        onClose={() => setSnack({ ...snack, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity={snack.severity} onClose={() => setSnack({ ...snack, open: false })}>
          {snack.message}
        </Alert>
      </Snackbar>
    </div>
  );
}
