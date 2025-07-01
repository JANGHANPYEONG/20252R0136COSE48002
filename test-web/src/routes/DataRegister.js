import React from 'react';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';

const DataRegister = () => {
    return (
        <Container maxWidth="md" style={{ marginTop: '100px' }}>
            <Typography variant="h4" sx={{ fontWeight: 600, color: '#151D48' }}>
                데이터등록
            </Typography>
        </Container>
    );
};

export default DataRegister; 