import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Tabs, Tab, Box } from '@mui/material';
import { Select, MenuItem } from '@mui/material';
import TasteTime from './Charts/Time/TasteTime';
import CorrelationChart from './Charts/Corr/CorrelationChart';
import HeatMapChart from './Charts/HeatMap/HeatMapChart';
import BoxPlotChart from './Charts/BoxPlot/BoxPlotChart';
import AgingBoxPlotChart from './Charts/BoxPlot/AgingBoxPlotChart';

const CustomTabPanel = (props) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
      style={{ backgroundColor: 'white' }}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

CustomTabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};

const a11yProps = (index) => {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
};

const StatsTabs = ({ startDate, endDate }) => {
  const [value, setValue] = useState(0);
  const [meatState, setMeatState] = useState('원육');
  const [animalType, setAnimalType] = useState('소');
  const [grade, setGrade] = useState('5');
  const [meatValue, setMeatValue] = useState('등심');
  const [seqnoValue, setSeqnoValue] = useState(1);
  const [modality, setModality] = useState('MSI');

  useEffect(() => {
    // console.log('stat tab' + startDate, '-', endDate);
  }, [startDate, endDate]);
  const handleChange = (event, newValue) => {
    setValue(newValue);
  };
  const handleMeatValueChange = (event) => {
    setMeatValue(event.target.value);
  };
  const handleSeqnoValueChange = (event) => {
    setSeqnoValue(event.target.value);
  };

  const handleMeatStateChange = (event) => {
    setMeatState(event.target.value);
  };

  // 동물별 선택 가능한 부위 목록
  const meatPartsByAnimal = {
    '소': ['등심', '안심', '갈비', '목심', '설도', '사태', '우둔', '앞다리'],
    '돼지': ['삼겹살', '목심', '등심', '앞다리', '뒷다리', '갈비', '항정살', '가브리살'],
    '닭': ['가슴살', '다리살', '날개', '안심', '넓적다리']
  };

  const handleAnimalChange = (event) => {
    const nextAnimal = event.target.value;
    setAnimalType(nextAnimal);
    setGrade('5');
    // 동물 변경 시 '전체'로 초기화 (부위 전체 선택)
    setMeatValue('전체');
  };
  const handleGradeChange = (event) => {
    setGrade(event.target.value);
  };
  const handleModalityChange = (event) => {
    setModality(event.target.value);
  };

  return (
    <Box sx={{ width: '900px', height: '350px' }}>
      <Box
        sx={{
          borderBottom: 1,
          borderColor: 'divider',
          backgroundColor: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <Tabs
          value={value}
          onChange={handleChange}
          textColor="secondary"
          indicatorColor="secondary"
        >
          <Tab label="통계" {...a11yProps(0)} />
          <Tab label="분포" {...a11yProps(1)} />
          <Tab label="상관관계" {...a11yProps(2)} />
          <Tab label="시계열" {...a11yProps(3)} />
          <Tab label="숙성도 비교 차트" {...a11yProps(4)} />
        </Tabs>
        <Box>
          <Select
            labelId="modality-label"
            id="modality"
            value={modality}
            onChange={handleModalityChange}
            label="데이터 소스"
            size="small"
            sx={{ mr: 1, '& .MuiSelect-select': { py: 0.5, px: 0.5 } }}
          >
            <MenuItem value="MSI">MSI</MenuItem>
            <MenuItem value="RGB">RGB</MenuItem>
          </Select>
          {value === 3 ? (
            <Box component="span">
              <Select
                labelId="animal-label"
                id="animal"
                value={animalType}
                onChange={handleAnimalChange}
                label="동물 종류"
                size="small"
                sx={{ mr: 1, '& .MuiSelect-select': { py: 0.5, px: 0.5 } }}
              >
                <MenuItem value="소">소</MenuItem>
                <MenuItem value="돼지">돼지</MenuItem>
                <MenuItem value="닭">닭</MenuItem>
              </Select>
              <Select
                labelId="meat-value-label"
                id="meat-value"
                value={meatValue}
                onChange={handleMeatValueChange}
                label="부위"
                size="small"
                sx={{ mr: 1, '& .MuiSelect-select': { py: 0.5, px: 0.5 } }}
              >
                <MenuItem value="전체">전체</MenuItem>
                {(meatPartsByAnimal[animalType] || []).map((part) => (
                  <MenuItem key={part} value={part}>{part}</MenuItem>
                ))}
              </Select>
              <Select
                labelId="seqno-label"
                id="seqno-value"
                value={seqnoValue}
                onChange={handleSeqnoValueChange}
                label="회차 정보"
                size="small"
                sx={{ '& .MuiSelect-select': { py: 0.5, px: 0.5 } }}
              >
                <MenuItem value="1">1회차</MenuItem>
                <MenuItem value="2">2회차</MenuItem>
                <MenuItem value="3">3회차</MenuItem>
                <MenuItem value="4">4회차</MenuItem>
              </Select>
            </Box>
          ) : value === 4 ? (
            <Box component="span">
              <Select
                labelId="animal-label"
                id="animal"
                value={animalType}
                onChange={handleAnimalChange}
                label="동물 종류"
                size="small"
                sx={{ mr: 1, '& .MuiSelect-select': { py: 0.5, px: 0.5 } }}
              >
                <MenuItem value="소">소</MenuItem>
                <MenuItem value="돼지">돼지</MenuItem>
                <MenuItem value="닭">닭</MenuItem>
              </Select>
              <Select
                labelId="meat-value-label-aging-top"
                id="meat-value-aging-top"
                value={meatValue}
                onChange={handleMeatValueChange}
                label="부위"
                size="small"
                sx={{ '& .MuiSelect-select': { py: 0.5, px: 0.5 } }}
              >
                <MenuItem value="전체">전체</MenuItem>
                {(meatPartsByAnimal[animalType] || []).map((part) => (
                  <MenuItem key={part} value={part}>{part}</MenuItem>
                ))}
              </Select>
            </Box>
          ) : (
            <Box component="span">
              <Select
                labelId="meat-state-label"
                id="meat-state"
                value={meatState}
                onChange={handleMeatStateChange}
                label="육류 가공 상태"
                size="small"
                sx={{ mr: 1, '& .MuiSelect-select': { py: 0.5, px: 0.5 } }}
              >
                <MenuItem value="원육">원육</MenuItem>
                <MenuItem value="처리육">처리육</MenuItem>
              </Select>
              <Select
                labelId="animal-label"
                id="animal"
                value={animalType}
                onChange={handleAnimalChange}
                label="동물 종류"
                size="small"
                sx={{ mr: 1, '& .MuiSelect-select': { py: 0.5, px: 0.5 } }}
              >
                <MenuItem value="소">소</MenuItem>
                <MenuItem value="돼지">돼지</MenuItem>
                <MenuItem value="닭">닭</MenuItem>
              </Select>
              <Select
                labelId="grade-label"
                id="grade"
                value={grade}
                onChange={handleGradeChange}
                label="등급"
                size="small"
                sx={{ mr: (value === 0 || value === 1 || value === 2) ? 1 : 0, '& .MuiSelect-select': { py: 0.5, px: 0.5 } }}              >
                <MenuItem value="5">전체</MenuItem>
                {animalType === '소' && <MenuItem value="0">1++</MenuItem>}
                {animalType === '소' && <MenuItem value="1">1+</MenuItem>}
                {animalType === '소' && <MenuItem value="2">1</MenuItem>}
                {animalType === '소' && <MenuItem value="3">2</MenuItem>}
                {animalType === '소' && <MenuItem value="4">3</MenuItem>}
              </Select>
              {(value === 0 || value === 1 || value === 2) && (
                <Select
                  labelId="meat-value-label-top"
                  id="meat-value-top"
                  value={meatValue}
                  onChange={handleMeatValueChange}
                  label="부위"
                  size="small"
                  sx={{ '& .MuiSelect-select': { py: 0.5, px: 0.5 } }}
                >
                  <MenuItem value="전체">전체</MenuItem>
                  {(meatPartsByAnimal[animalType] || []).map((part) => (
                    <MenuItem key={part} value={part}>{part}</MenuItem>
                  ))}
                </Select>
              )}
            </Box>
          )}
        </Box>
      </Box>

      <CustomTabPanel value={value} index={0}>
        <Box>
          <BoxPlotChart
            key={`sens-${startDate}-${endDate}-${animalType}-${grade}-${meatState}-${modality}`}
            meatState={meatState}
            dataType="sensory"
            startDate={startDate}
            endDate={endDate}
            animalType={animalType}
            grade={grade}
            modality={modality}
            meatValue={meatValue}
          />
          {meatState !== '가열육' && (
            <BoxPlotChart
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}-${meatState}-${modality}`}
              meatState={meatState}
              dataType="taste"
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
              modality={modality}
              meatValue={meatValue}
            />
          )}
        </Box>
      </CustomTabPanel>

      <CustomTabPanel value={value} index={1}>
        <Box>
          <HeatMapChart
            key={`sens-${startDate}-${endDate}-${animalType}-${grade}-${meatState}-${modality}`}
            meatState={meatState}
            dataType="sensory"
            startDate={startDate}
            endDate={endDate}
            animalType={animalType}
            grade={grade}
            modality={modality}
            meatValue={meatValue}
          />
          {meatState !== '가열육' && (
            <HeatMapChart
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}-${meatState}-${modality}`}
              meatState={meatState}
              dataType="taste"
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
              modality={modality}
              meatValue={meatValue}
            />
          )}
        </Box>
      </CustomTabPanel>

      <CustomTabPanel value={value} index={2}>
        <Box>
          <CorrelationChart
            key={`sens-${startDate}-${endDate}-${animalType}-${grade}-${meatState}-${modality}-${meatValue}`}
            meatState={meatState}
            dataType="sensory"
            startDate={startDate}
            endDate={endDate}
            animalType={animalType}
            grade={grade}
            modality={modality}
            meatValue={meatValue}
          />
          {meatState !== '가열육' && (
            <CorrelationChart
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}-${meatState}-${modality}-${meatValue}`}
              meatState={meatState}
              dataType="taste"
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
              modality={modality}
              meatValue={meatValue}
            />
          )}
        </Box>
      </CustomTabPanel>

      <CustomTabPanel value={value} index={3}>
        <Box>
          <TasteTime
            key={`sens-time-${startDate}-${endDate}-${seqnoValue}-${meatValue}-${modality}`}
            startDate={startDate}
            endDate={endDate}
            seqnoValue={seqnoValue}
            meatValue={meatValue}
            dataType="sensory"
            modality={modality}
          />
          <TasteTime
            key={`pred-time-${startDate}-${endDate}-${seqnoValue}-${meatValue}-${modality}`}
            startDate={startDate}
            endDate={endDate}
            seqnoValue={seqnoValue}
            meatValue={meatValue}
            dataType="taste"
            modality={modality}
          />
        </Box>
      </CustomTabPanel>

      <CustomTabPanel value={value} index={4}>
        <Box>
          <AgingBoxPlotChart
            key={`sens-aging-${startDate}-${endDate}-${animalType}-${grade}-${meatState}-${modality}`}
            meatState={meatState}
            dataType="sensory"
            startDate={startDate}
            endDate={endDate}
            animalType={animalType}
            grade={grade}
            modality={modality}
            meatValue={meatValue}
          />
          {meatState !== '가열육' && (
            <AgingBoxPlotChart
              key={`taste-aging-${startDate}-${endDate}-${animalType}-${grade}-${meatState}-${modality}`}
              meatState={meatState}
              dataType="taste"
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
              modality={modality}
              meatValue={meatValue}
            />
          )}
        </Box>
      </CustomTabPanel>
    </Box>
  );
};

export default StatsTabs;
