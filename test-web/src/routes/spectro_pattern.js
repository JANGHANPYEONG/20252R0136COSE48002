import React, { useState } from 'react';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';
import Divider from '@mui/material/Divider';
import ImageUploadBox from '../components/SpectroPattern/ImageUploadBox';
import ClusteringResultBox from '../components/SpectroPattern/ClusteringResultBox';
import PatternGraph from '../components/SpectroPattern/PatternGraph';
import HistoryIcon from '@mui/icons-material/History';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import InsightsIcon from '@mui/icons-material/Insights';

const dummyPastData = [
    { date: '2025-05-10', id: 1 }
];

const dummyGraphData = {
    x: Array.from({ length: 21 }, (_, i) => 600 + i * 20),
    y: [10, 15, 13, 20, 18, 70, 30, 28, 35, 40, 70, 45, 42, 38, 35, 30, 28, 65, 20, 15, 10],
    peaks: [3, 7, 11]
};

const SpectroPattern = () => {
    const [showUploadBox, setShowUploadBox] = useState(false);
    const [selectedData, setSelectedData] = useState(null);
    const [selectedPeak, setSelectedPeak] = useState(null);

    return (
        <Box sx={{ minHeight: '100vh', background: '#F6F8FA', pt: 20, px: { xs: 1, sm: 2, md: 4, lg: 6 }, maxWidth: '1600px', mx: 'auto' }}>
            <Grid container spacing={6} justifyContent="center">
                <Grid item xs={12} md={4} lg={3}>
                    <Stack spacing={4} sx={{ mx: 'auto', maxWidth: 320 }} divider={<Divider flexItem sx={{ borderColor: '#e0e0e0' }} />}>
                        <Box>
                            <Typography variant="h4" sx={{ fontWeight: 800, color: '#222', letterSpacing: -1, lineHeight: 1.3 }}>
                                분광 데이터<br />패턴 분석
                            </Typography>
                            <Typography variant="body2" sx={{ mt: 1.5, color: '#555', lineHeight: 1.6 }}>
                                이미지 업로드부터 분석 결과까지 한눈에 확인하세요.
                            </Typography>
                        </Box>

                        <Box>
                            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                                <UploadFileIcon fontSize="small" color="primary" /> 이미지 업로드
                            </Typography>
                            <Button
                                variant="contained"
                                size="large"
                                fullWidth
                                sx={{
                                    borderRadius: 2,
                                    fontWeight: 700,
                                    boxShadow: 1,
                                    backgroundColor: '#1976d2',
                                    '&:hover': { backgroundColor: '#1565c0' },
                                }}
                                onClick={() => setShowUploadBox(v => !v)}
                            >
                                이미지 업로드
                            </Button>
                            {showUploadBox && (
                                <Box sx={{ mt: 2 }}>
                                    <ImageUploadBox />
                                </Box>
                            )}
                        </Box>

                        <Box>
                            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                                <HistoryIcon fontSize="small" color="primary" /> 지난 데이터
                            </Typography>
                            <Stack spacing={1}>
                                {dummyPastData.map(d => (
                                    <Button
                                        key={d.id}
                                        variant={selectedData === d.id ? 'contained' : 'outlined'}
                                        size="large"
                                        fullWidth
                                        sx={{
                                            borderRadius: 2,
                                            fontWeight: 600,
                                            boxShadow: selectedData === d.id ? 2 : 0,
                                            background: selectedData === d.id ? '#1976d2' : '#fff',
                                            color: selectedData === d.id ? '#fff' : '#222',
                                            textTransform: 'none',
                                            transition: 'all 0.15s',
                                            '&:hover': {
                                                background: selectedData === d.id ? '#1565c0' : '#f0f4fa',
                                            },
                                        }}
                                        onClick={() => {
                                            setSelectedData(d.id);
                                            setSelectedPeak(null);
                                        }}
                                    >
                                        {d.date}
                                    </Button>
                                ))}
                            </Stack>
                        </Box>
                    </Stack>
                </Grid>

                <Grid item xs={12} md={8} lg={9}>
                    <Box sx={{ width: '100%', maxWidth: '100%', minHeight: 500, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                        {selectedData ? (
                            <Paper elevation={3} sx={{ width: '100%', maxWidth: 900, p: { xs: 3, md: 5 }, borderRadius: 4, mb: 4 }}>
                                <Stack spacing={4}>
                                    <Box>
                                        <Typography variant="h6" sx={{ fontWeight: 700, mb: 2, color: '#222' }}>
                                            600~1000 파장 그래프
                                        </Typography>
                                        <PatternGraph
                                            data={dummyGraphData}
                                            peaks={dummyGraphData.peaks}
                                            onPeakClick={setSelectedPeak}
                                        />
                                        <Typography variant="body2" sx={{ mt: 2, color: '#1976d2', fontWeight: 600, textAlign: 'center' }}>
                                            그래프에서 진한 파란색 막대(극점)를 클릭하면 클러스터링 결과가 표시됩니다.
                                        </Typography>
                                        {selectedPeak !== null && (
                                            <Box sx={{ mt: 3 }}>
                                                <ClusteringResultBox />
                                            </Box>
                                        )}
                                    </Box>

                                    <Box sx={{ p: 3, background: '#f7faff', borderRadius: 3, boxShadow: 1 }}>
                                        <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <InsightsIcon fontSize="small" color="primary" /> 패턴 분석 정리
                                        </Typography>
                                        <Stack spacing={1} component="ul" sx={{ m: 0, p: 0, fontSize: 16, color: '#333', fontWeight: 500 }}>
                                            <li><span style={{ color: '#1976d2', fontWeight: 700 }}>패턴 유력 후보 구역 1:</span> 640nm ~ 660nm</li>
                                            <li><span style={{ color: '#1976d2', fontWeight: 700 }}>패턴 유력 후보 구역 2:</span> 740nm ~ 760nm</li>
                                            <li><span style={{ color: '#1976d2', fontWeight: 700 }}>패턴 유력 후보 구역 3:</span> 800nm ~ 820nm</li>
                                        </Stack>
                                    </Box>
                                </Stack>
                            </Paper>
                        ) : (
                            <Paper elevation={0} sx={{ width: '100%', maxWidth: 900, p: { xs: 3, md: 5 }, borderRadius: 4, color: '#aaa', textAlign: 'center', minHeight: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <Typography variant="h6" sx={{ fontWeight: 500 }}>
                                    왼쪽에서 데이터를 선택하면 결과가 여기에 표시됩니다.
                                </Typography>
                            </Paper>
                        )}
                    </Box>
                </Grid>
            </Grid>
        </Box>
    );
};

export default SpectroPattern;
