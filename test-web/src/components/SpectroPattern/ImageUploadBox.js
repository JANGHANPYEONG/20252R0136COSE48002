import React, { useRef, useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const ImageUploadBox = () => {
    const fileInputRef = useRef();
    const [fileName, setFileName] = useState('');
    const [dragActive, setDragActive] = useState(false);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFileName(e.target.files[0].name);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragActive(true);
    };
    const handleDragLeave = (e) => {
        e.preventDefault();
        setDragActive(false);
    };
    const handleDrop = (e) => {
        e.preventDefault();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFileName(e.dataTransfer.files[0].name);
        }
    };

    return (
        <Box
            sx={{
                border: dragActive ? '2px solid #1976d2' : '2px dashed #bdbdbd',
                borderRadius: 3,
                p: 4,
                background: dragActive ? '#e3f2fd' : '#fafbfc',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 2,
                boxShadow: 2,
                transition: 'all 0.2s',
                cursor: 'pointer',
            }}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current.click()}
        >
            <CloudUploadIcon sx={{ fontSize: 48, color: '#1976d2', mb: 1 }} />
            <Typography variant="body1" sx={{ fontWeight: 600, color: '#1976d2' }}>
                이미지를 드래그하거나 클릭해서 업로드하세요
            </Typography>
            <input
                type="file"
                accept="image/*"
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={handleFileChange}
            />
            <Typography variant="body2" color="text.secondary">
                {fileName ? `선택된 파일: ${fileName}` : '선택된 파일 없음'}
            </Typography>
            <Button variant="contained" disabled={!fileName} sx={{ borderRadius: 2, fontWeight: 700, width: 180 }}>
                업로드
            </Button>
        </Box>
    );
};

export default ImageUploadBox; 