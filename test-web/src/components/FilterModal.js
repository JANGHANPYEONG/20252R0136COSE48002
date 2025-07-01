import React, { useState } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Box,
    Typography,
    IconButton,
    Chip,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Grid,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { Add as AddIcon, Delete as DeleteIcon } from '@mui/icons-material';

const FilterModal = ({ open, onClose, onApply, filters, setFilters }) => {
    const [newFilterName, setNewFilterName] = useState('');
    const [newFilterOptions, setNewFilterOptions] = useState('');
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);

    // 날짜 필터는 항상 존재
    const dateFilter = filters.find(f => f.name === '날짜') || {
        name: '날짜',
        type: 'date',
        options: [],
        value: { start: null, end: null }
    };

    const handleAddFilter = () => {
        if (newFilterName.trim() && newFilterOptions.trim()) {
            const options = newFilterOptions.split(',').map(opt => opt.trim());
            const newFilter = {
                name: newFilterName.trim(),
                type: 'select',
                options: options,
                value: ''
            };

            setFilters(prev => [...prev.filter(f => f.name !== newFilterName.trim()), newFilter]);
            setNewFilterName('');
            setNewFilterOptions('');
        }
    };

    const handleDeleteFilter = (filterName) => {
        setFilters(prev => prev.filter(f => f.name !== filterName));
    };

    const handleFilterValueChange = (filterName, value) => {
        setFilters(prev => prev.map(f =>
            f.name === filterName ? { ...f, value } : f
        ));
    };

    const handleDateChange = (type, date) => {
        if (type === 'start') {
            setStartDate(date);
            handleFilterValueChange('날짜', { start: date, end: endDate });
        } else {
            setEndDate(date);
            handleFilterValueChange('날짜', { start: startDate, end: date });
        }
    };

    const handleApply = () => {
        const appliedFilters = filters.map(f => ({
            ...f,
            value: f.name === '날짜' ? { start: startDate, end: endDate } : f.value
        }));
        onApply(appliedFilters);
        onClose();
    };

    const handleReset = () => {
        setFilters([{
            name: '날짜',
            type: 'date',
            options: [],
            value: { start: null, end: null }
        }]);
        setStartDate(null);
        setEndDate(null);
    };

    // dayjs 날짜를 문자열로 변환하는 함수
    const formatDate = (date) => {
        if (!date) return '';
        return date.format('YYYY-MM-DD');
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
            <DialogTitle>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="h6">필터 설정</Typography>
                    <Button onClick={handleReset} color="secondary" size="small">
                        초기화
                    </Button>
                </Box>
            </DialogTitle>

            <DialogContent>
                <LocalizationProvider dateAdapter={AdapterDayjs}>
                    {/* 날짜 필터 */}
                    <Box mb={3}>
                        <Typography variant="subtitle1" gutterBottom>
                            날짜 범위 *
                        </Typography>
                        <Grid container spacing={2}>
                            <Grid item xs={6}>
                                <DatePicker
                                    label="시작일"
                                    value={startDate}
                                    onChange={(date) => handleDateChange('start', date)}
                                    slotProps={{
                                        textField: {
                                            fullWidth: true,
                                        },
                                    }}
                                />
                            </Grid>
                            <Grid item xs={6}>
                                <DatePicker
                                    label="종료일"
                                    value={endDate}
                                    onChange={(date) => handleDateChange('end', date)}
                                    slotProps={{
                                        textField: {
                                            fullWidth: true,
                                        },
                                    }}
                                />
                            </Grid>
                        </Grid>
                    </Box>

                    {/* 기존 필터들 */}
                    {filters.filter(f => f.name !== '날짜').map((filter) => (
                        <Box key={filter.name} mb={2}>
                            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                                <Typography variant="subtitle1">{filter.name}</Typography>
                                <IconButton
                                    size="small"
                                    onClick={() => handleDeleteFilter(filter.name)}
                                    color="error"
                                >
                                    <DeleteIcon />
                                </IconButton>
                            </Box>
                            <FormControl fullWidth>
                                <InputLabel>{filter.name} 선택</InputLabel>
                                <Select
                                    value={filter.value}
                                    onChange={(e) => handleFilterValueChange(filter.name, e.target.value)}
                                    label={`${filter.name} 선택`}
                                >
                                    <MenuItem value="">전체</MenuItem>
                                    {filter.options.map((option) => (
                                        <MenuItem key={option} value={option}>
                                            {option}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        </Box>
                    ))}

                    {/* 새 필터 추가 */}
                    <Box mt={3} p={2} border={1} borderColor="grey.300" borderRadius={1}>
                        <Typography variant="subtitle1" gutterBottom>
                            새 필터 추가
                        </Typography>
                        <Grid container spacing={2} alignItems="flex-end">
                            <Grid item xs={4}>
                                <TextField
                                    label="필터명"
                                    value={newFilterName}
                                    onChange={(e) => setNewFilterName(e.target.value)}
                                    fullWidth
                                    size="small"
                                />
                            </Grid>
                            <Grid item xs={6}>
                                <TextField
                                    label="옵션들 (쉼표로 구분)"
                                    value={newFilterOptions}
                                    onChange={(e) => setNewFilterOptions(e.target.value)}
                                    fullWidth
                                    size="small"
                                    placeholder="예: 소, 돼지, 닭"
                                />
                            </Grid>
                            <Grid item xs={2}>
                                <Button
                                    variant="contained"
                                    onClick={handleAddFilter}
                                    disabled={!newFilterName.trim() || !newFilterOptions.trim()}
                                    startIcon={<AddIcon />}
                                    fullWidth
                                >
                                    추가
                                </Button>
                            </Grid>
                        </Grid>
                    </Box>

                    {/* 현재 적용된 필터 표시 */}
                    {filters.some(f => f.value && (f.type === 'select' ? f.value !== '' : true)) && (
                        <Box mt={3}>
                            <Typography variant="subtitle2" gutterBottom>
                                적용된 필터:
                            </Typography>
                            <Box display="flex" flexWrap="wrap" gap={1}>
                                {filters.map((filter) => {
                                    if (filter.name === '날짜' && startDate && endDate) {
                                        return (
                                            <Chip
                                                key={filter.name}
                                                label={`${filter.name}: ${formatDate(startDate)} ~ ${formatDate(endDate)}`}
                                                onDelete={() => {
                                                    setStartDate(null);
                                                    setEndDate(null);
                                                    handleFilterValueChange('날짜', { start: null, end: null });
                                                }}
                                                color="primary"
                                                variant="outlined"
                                            />
                                        );
                                    } else if (filter.type === 'select' && filter.value) {
                                        return (
                                            <Chip
                                                key={filter.name}
                                                label={`${filter.name}: ${filter.value}`}
                                                onDelete={() => handleFilterValueChange(filter.name, '')}
                                                color="primary"
                                                variant="outlined"
                                            />
                                        );
                                    }
                                    return null;
                                })}
                            </Box>
                        </Box>
                    )}
                </LocalizationProvider>
            </DialogContent>

            <DialogActions>
                <Button onClick={onClose}>취소</Button>
                <Button onClick={handleApply} variant="contained">
                    적용
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default FilterModal; 