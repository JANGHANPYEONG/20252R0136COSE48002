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
        { name: '품종', options: ['소', '돼지', '닭'] },
        { name: '지역', options: ['서울', '부산', '대구', '인천', '광주', '대전', '울산'] },
    ];

    // 품종을 categoryIds로 변환하는 함수 (DB 모델에 정확히 맞게 수정)
    const getCategoryIds = (specieValue) => {
        switch (specieValue) {
            case '소':
                // 소: DB의 CategoryInfo.id 값들 (speciesId = 0)
                // calId(id, s_id, 0) = 100 * 0 + 10 * id + s_id
                // 대분할별로 모든 소분할 ID 생성
                const cattleIds = [];
                for (let largeId = 0; largeId <= 9; largeId++) { // 0~9 (대분할)
                    const maxSmallId = largeId === 0 ? 0 : // 안심: 1개
                                    largeId === 1 ? 3 : // 등심: 4개
                                    largeId === 2 ? 0 : // 채끝: 1개
                                    largeId === 3 ? 0 : // 목심: 1개
                                    largeId === 4 ? 4 : // 앞다리: 5개
                                    largeId === 5 ? 1 : // 우둔: 2개
                                    largeId === 6 ? 4 : // 설도: 5개
                                    largeId === 7 ? 6 : // 양지: 7개
                                    largeId === 8 ? 2 : // 사태: 3개
                                    largeId === 9 ? 7 : 0; // 갈비: 8개
                    
                    for (let smallId = 0; smallId <= maxSmallId; smallId++) {
                        cattleIds.push(100 * 0 + 10 * largeId + smallId);
                    }
                }
                return cattleIds;
                
            case '돼지':
                // 돼지: DB의 CategoryInfo.id 값들 (speciesId = 1)
                // calId(id, s_id, 1) = 100 * 1 + 10 * id + s_id
                const pigIds = [];
                for (let largeId = 0; largeId <= 6; largeId++) { // 0~6 (대분할)
                    const maxSmallId = largeId === 0 ? 0 : // 안심: 1개
                                    largeId === 1 ? 1 : // 등심: 2개
                                    largeId === 2 ? 0 : // 목심: 1개
                                    largeId === 3 ? 5 : // 앞다리: 6개
                                    largeId === 4 ? 2 : // 갈비: 3개
                                    largeId === 5 ? 4 : // 삼겹살: 5개
                                    largeId === 6 ? 0 : 0; // 뒷다리: 1개
                    
                    for (let smallId = 0; smallId <= maxSmallId; smallId++) {
                        pigIds.push(100 * 1 + 10 * largeId + smallId);
                    }
                }
                return pigIds;
                
            case '닭':
                // 닭: 아직 DB에 정의되지 않음 (빈 배열 반환)
                return [];
                
            default:
                return [];
        }
    };

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
        // 품종 필터에서 categoryIds 생성
        const specieFilter = filters.find(f => f.name === '품종');
        const categoryIds = specieFilter && specieFilter.value ? getCategoryIds(specieFilter.value) : [];

        // 백엔드가 기대하는 필터 구조로 변환
        const appliedFilters = [
            {
                name: '날짜',
                type: 'date',
                options: [],
                value: {
                    start: startDate ? startDate.format('YYYY-MM-DD') : null,
                    end: endDate ? endDate.format('YYYY-MM-DD') : null
                }
            },
            {
                name: '품종',
                type: 'select',
                options: ['소', '돼지', '닭'],
                value: specieFilter ? specieFilter.value : '',
                categoryIds: categoryIds
            },
            {
                name: 'page',
                type: 'select',
                options: [1, 2, 3, 4, 5],
                value: filters.page || 1
            },
            {
                name: 'pageSize',
                type: 'select',
                options: [10, 25, 50, 100],
                value: filters.pageSize || 50
            }
        ];

        onApply(appliedFilters);
        onClose();
    };

    const handleReset = () => {
        setFilters([{
            name: '날짜',
            type: 'date',
            options: [],
            value: { start: null, end: null }
        }, {
            name: 'page',
            type: 'select',
            options: [1, 2, 3, 4, 5],
            value: 1
        }, {
            name: 'pageSize',
            type: 'select',
            options: [10, 25, 50, 100],
            value: 50
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

                    {/* 페이지네이션 옵션 */}
                    <Box mb={3}>
                        <Typography variant="subtitle1" gutterBottom>
                            페이지네이션
                        </Typography>
                        <Grid container spacing={2}>
                            <Grid item xs={6}>
                                <FormControl fullWidth>
                                    <InputLabel>페이지 크기</InputLabel>
                                    <Select
                                        value={filters.pageSize || 50}
                                        onChange={(e) => handleFilterValueChange('pageSize', e.target.value)}
                                        label="페이지 크기"
                                    >
                                        <MenuItem value={10}>10개</MenuItem>
                                        <MenuItem value={25}>25개</MenuItem>
                                        <MenuItem value={50}>50개</MenuItem>
                                        <MenuItem value={100}>100개</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                            <Grid item xs={6}>
                                <FormControl fullWidth>
                                    <InputLabel>페이지 번호</InputLabel>
                                    <Select
                                        value={filters.page || 1}
                                        onChange={(e) => handleFilterValueChange('page', e.target.value)}
                                        label="페이지 번호"
                                    >
                                        <MenuItem value={1}>1페이지</MenuItem>
                                        <MenuItem value={2}>2페이지</MenuItem>
                                        <MenuItem value={3}>3페이지</MenuItem>
                                        <MenuItem value={4}>4페이지</MenuItem>
                                        <MenuItem value={5}>5페이지</MenuItem>
                                    </Select>
                                </FormControl>
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