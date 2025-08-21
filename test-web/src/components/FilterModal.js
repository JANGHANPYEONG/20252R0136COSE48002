import React, { useState } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Box,
    Typography,
    IconButton,
    Chip,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Grid,
    Tabs,
    Tab,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { Delete as DeleteIcon } from '@mui/icons-material';
import dayjs from 'dayjs';

const FilterModal = ({ open, onClose, onApply, filters, setFilters }) => {
    const [startDate, setStartDate] = useState(null);
    const [endDate, setEndDate] = useState(null);
    const [duration, setDuration] = useState('week'); // 기간 선택 상태 추가

    // 기간별 날짜 계산 함수
    const calculateDateRange = (durationType) => {
        const today = dayjs();
        let start, end;
        
        switch (durationType) {
            case 'week':
                start = today.subtract(7, 'day');
                end = today;
                break;
            case 'month':
                start = today.subtract(1, 'month');
                end = today;
                break;
            case 'quarter':
                start = today.subtract(3, 'month');
                end = today;
                break;
            case 'year':
                start = today.subtract(1, 'year');
                end = today;
                break;
            case 'all':
                start = null;
                end = null;
                break;
            default:
                start = today.subtract(7, 'day');
                end = today;
        }
        
        return { start, end };
    };

    // 기간 탭 변경 핸들러
    const handleDurationChange = (event, newValue) => {
        setDuration(newValue);
        const { start, end } = calculateDateRange(newValue);
        setStartDate(start);
        setEndDate(end);
        handleFilterValueChange('날짜', { start, end });
    };

    // 필터 후보 목록 - 사용자가 선택할 수 있는 필터들
    const filterCandidates = [
        { name: '데이터 타입', options: ['RGB', 'MSI'] },
        { name: '품종', options: ['소', '돼지', '닭'] },
        { name: '지역', options: ['서울', '부산', '대구', '인천', '광주', '대전', '울산'] },
    ];

    // 날짜 필터는 항상 존재
    const dateFilter = filters.find(f => f.name === '날짜') || {
        name: '날짜',
        type: 'date',
        options: [],
        value: { start: null, end: null }
    };

    // 선택된 필터 후보를 실제 필터로 추가
    const handleAddSelectedFilter = (filterName) => {
        if (!filterName) return; // 빈 값 선택 시 무시
        
        const selectedCandidate = filterCandidates.find(f => f.name === filterName);
        if (selectedCandidate) {
            // 이미 존재하는 필터인지 확인
            const existingFilter = filters.find(f => f.name === filterName);
            if (!existingFilter) {
                const newFilter = {
                    name: selectedCandidate.name,
                    type: 'select',
                    options: selectedCandidate.options,
                    value: ''
                };
                setFilters(prev => [...prev, newFilter]);
            }
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
        setDuration('week'); // 기간도 초기화
    };

    // dayjs 날짜를 문자열로 변환하는 함수
    const formatDate = (date) => {
        if (!date) return '';
        return date.format('YYYY-MM-DD');
    };

    // 이미 추가된 필터들의 이름 목록
    const addedFilterNames = filters.filter(f => f.name !== '날짜').map(f => f.name);
    
    // 아직 추가되지 않은 필터 후보들만 표시
    const availableCandidates = filterCandidates.filter(candidate => 
        !addedFilterNames.includes(candidate.name)
    );

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
                    {/* 기간 선택 탭 추가 */}
                    <Box mb={3}>
                        <Typography variant="subtitle1" gutterBottom>
                            조회 기간
                        </Typography>
                        <Tabs 
                            value={duration} 
                            onChange={handleDurationChange}
                            variant="fullWidth"
                            sx={{
                                '& .MuiTab-root': {
                                    minHeight: '40px',
                                    fontSize: '0.875rem',
                                    fontWeight: '500',
                                },
                                '& .Mui-selected': {
                                    color: '#1976d2',
                                    fontWeight: '600',
                                },
                                '& .MuiTabs-indicator': {
                                    backgroundColor: '#1976d2',
                                }
                            }}
                        >
                            <Tab label="1주" value="week" />
                            <Tab label="1개월" value="month" />
                            <Tab label="1분기" value="quarter" />
                            <Tab label="1년" value="year" />
                            <Tab label="전체" value="all" />
                        </Tabs>
                    </Box>

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
                        {duration !== 'all' && startDate && endDate && (
                            <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                                선택된 기간: {formatDate(startDate)} ~ {formatDate(endDate)}
                            </Typography>
                        )}
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

                    {/* 새 필터 추가 (드롭다운 방식) */}
                    {availableCandidates.length > 0 && (
                        <Box mt={3} p={2} border={1} borderColor="grey.300" borderRadius={1}>
                            <Typography variant="subtitle1" gutterBottom>
                                필터 추가
                            </Typography>
                            <FormControl fullWidth>
                                <InputLabel>필터 선택</InputLabel>
                                <Select
                                    value=""
                                    onChange={(e) => handleAddSelectedFilter(e.target.value)}
                                    label="필터 선택"
                                >
                                    <MenuItem value="">필터를 선택하세요</MenuItem>
                                    {availableCandidates.map((candidate) => (
                                        <MenuItem key={candidate.name} value={candidate.name}>
                                            {candidate.name} ({candidate.options.join(', ')})
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                            <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                                * 선택한 필터는 자동으로 추가됩니다
                            </Typography>
                        </Box>
                    )}

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