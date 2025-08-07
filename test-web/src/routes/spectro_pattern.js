import { useState } from 'react';
import { Box, Button, CircularProgress, Typography } from '@mui/material';
// style
import style from './style/dashboardstyle';
// components
import DataList from '../components/DataList';
import FilterModal from '../components/FilterModal';
//component/Charts/WavelengthChart추가 후 component가져오기
import WavelengthChart from '../components/Charts/WavelengthChart';
import { MenuItem, Select, FormControl, InputLabel } from '@mui/material';
const navy = '#0F3659';

const Spectro_pattern = () => {
    const [value, setValue] = useState('photo');
    const [data, setData] = useState([]);
    const [models, setModels] = useState([]);
    const [loading, setLoading] = useState(false);
    const [filterModalOpen, setFilterModalOpen] = useState(false);
    const [filters, setFilters] = useState([{
        name: '날짜',
        type: 'date',
        options: [],
        value: { start: null, end: null }
    }]);
    //그래프 상태 추가
    const [selectedFeature, setSelectedFeature] = useState('');
    const [importanceData, setImportanceData] = useState([]);
    
    //특성 선책 핸들러

    const handleFeatureChange = (event) => {
    const feature = event.target.value;
    setSelectedFeature(feature);

    // 예시: 해당 특성에 대한 중요도 데이터 가져오기 (임시 가짜 데이터)
    const dummy = Array.from({ length: 50 }, (_, i) => ({
        wavelength: 400 + i * 10,
        importance: Math.random(), // 추후 API 결과로 교체 가능
    }));
    setImportanceData(dummy);
};

    const handleValueChange = (newValue) => {
        setValue(newValue);
    };

    // 데이터 불러오기 함수
    const handleLoadData = () => {
        setLoading(true);
        // 실제 API 호출 로직이 여기에 들어갈 예정
        setTimeout(() => {
            setData([
                { id: 1, name: '데이터1', type: '사진', date: '2024-01-01' },
                { id: 2, name: '데이터2', type: '사진', date: '2024-01-02' },
            ]);
            setLoading(false);
        }, 1000);
    };

    // 필터 함수
    const handleFilter = () => {
        setFilterModalOpen(true);
    };

    // 필터 적용 함수
    const handleApplyFilters = (appliedFilters) => {
        setFilters(appliedFilters);
        console.log('적용된 필터:', appliedFilters);
        // 여기서 필터링된 데이터를 API로 요청
        handleLoadData(); // 필터 적용 후 데이터 다시 로드
    };

    // 학습하기 함수
    const handleTrain = () => {
        console.log('학습 시작');
    };

    // 탭별 컬럼 설정
    const getColumns = () => {
        switch (value) {
            case 'photo':
                return ['ID', '파일명', '회차', '날짜', '마블링', '수분도', '총점'];
            case 'spectral':
                return ['ID', '스펙트럼', '파장', '날짜'];
            case 'cross':
                return ['ID', '사진ID', '스펙트럼ID', '날짜'];
            default:
                return ['ID', '이름', '타입', '날짜'];
        }
    };

    // 탭별 모델 컬럼 설정
    const getModelColumns = () => {
        return ['모델명', '생성일', '정확도', '상태'];
    };

    return (
        <div
            style={{
                overflow: 'auto',
                width: '100%',
                marginTop: '100px',
                height: '100%',
                paddingLeft: '30px',
                paddingRight: '20px',
            }}
        >
            {/**페이지 제목 */}
            <Box
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    minWidth: '634px',
                }}
            >
                <span
                    style={{ color: `${navy}`, fontSize: '30px', fontWeight: '600' }}
                >
                    Pattern analysis
                </span>
            </Box>

            <Box sx={{ marginTop: '30px' }}>
                <Box>
                    {/* 버튼 영역 */}
                    <Box sx={{ display: 'flex', gap: 2, marginBottom: '20px' }}>
                        <Button
                            variant="contained"
                            onClick={handleLoadData}
                            disabled={loading}
                            sx={{
                                backgroundColor: navy,
                                '&:hover': { backgroundColor: '#0a2a4a' }
                            }}
                        >
                            {loading ? <CircularProgress size={20} color="inherit" /> : '데이터 불러오기'}
                        </Button>
                        <Button
                            variant="outlined"
                            onClick={handleFilter}
                            sx={{ borderColor: navy, color: navy }}
                        >
                            필터
                        </Button>
                    </Box>

                    {/* 데이터 리스트 */}
                    <DataList
                        columns={getColumns()}
                        data={data}
                        title="사진 데이터 목록"
                    />

                    {/* 데이터 개수 */}
                    <Typography sx={{ marginTop: '10px', color: navy }}>
                        총 {data.length}개의 데이터
                    </Typography>

                    {/* 학습하기 버튼 */}
                    <Box sx={{ marginTop: '20px', marginBottom: '20px' }}>
                        <Button
                            variant="contained"
                            onClick={handleTrain}
                            disabled={data.length === 0}
                            sx={{
                                backgroundColor: '#28a745',
                                '&:hover': { backgroundColor: '#218838' },
                                '&:disabled': { backgroundColor: '#6c757d' }
                            }}
                        >
                            분석하기
                        </Button>
                    </Box>
                    <Box sx={{ marginTop: '40px' }}>
                        <Typography variant="h6" sx={{ color: navy, marginBottom: '10px' }}>
                            특성별 파장 연관도
                        </Typography>

                        <FormControl sx={{ minWidth: 200, marginBottom: 2 }}>
                            <InputLabel>특성 선택</InputLabel>
                            <Select value={selectedFeature} label="특성 선택" onChange={handleFeatureChange}>
                                <MenuItem value="맛">맛</MenuItem>
                                <MenuItem value="육색">육색</MenuItem>
                                <MenuItem value="부패정도">부패정도</MenuItem>
                            </Select>
                        </FormControl>

                        {importanceData.length > 0 && (
                            <WavelengthChart data={importanceData} />
                        )}
                    </Box>                   
                </Box>
            </Box>

            {/* 필터 모달 */}
            <FilterModal
                open={filterModalOpen}
                onClose={() => setFilterModalOpen(false)}
                onApply={handleApplyFilters}
                filters={filters}
                setFilters={setFilters}
            />
        </div>
    );
};

export default Spectro_pattern; 