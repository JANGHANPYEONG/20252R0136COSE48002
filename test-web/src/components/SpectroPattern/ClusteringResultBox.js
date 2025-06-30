import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';

const ClusteringResultBox = () => (
    <Box sx={{ p: 2, border: '1px solid #1976d2', borderRadius: 2, background: '#e3f2fd' }}>
        <Typography variant="subtitle1" sx={{ mb: 1 }}>클러스터링 결과</Typography>
        <Typography color="text.secondary">(여기에 클러스터링 결과가 표시됩니다)</Typography>
    </Box>
);

export default ClusteringResultBox; 