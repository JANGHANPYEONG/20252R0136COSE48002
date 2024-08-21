import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Tabs, Tab, Box } from '@mui/material';
import { Select, MenuItem } from '@mui/material';
import TasteTime from './Charts/Time/TasteTime';
import CorrelationChart from './Charts/Corr/CorrelationChart';
import HeatMapChart from './Charts/HeatMap/HeatMapChart';
import BoxPlotChart from './Charts/BoxPlot/BoxPlotChart';

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
  // const [slot, setSlot] = useState('week');
  // const [alignment, setAlignment] = useState('맛');
  // const [gradeAlignment, setGradeAlignment] = useState('소');
  const [meatState, setMeatState] = useState('원육');
  const [animalType, setAnimalType] = useState('소');
  const [grade, setGrade] = useState('5');
  const [meatValue, setMeatValue] = useState('등심');
  const [seqnoValue, setSeqnoValue] = useState(1);

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
  // const handleFirstChange = (event) => {
  //   setAlignment(event.target.value);
  //   setMeatState('원육'); // Initialize meatState to "원육"
  // };

  const handleMeatStateChange = (event) => {
    setMeatState(event.target.value);
  };

  const handleAnimalChange = (event) => {
    setAnimalType(event.target.value);
    setGrade('5'); // 등급을 '전체'로 초기화
  };
  const handleGradeChange = (event) => {
    setGrade(event.target.value);
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
        </Tabs>
        <Box>
          {value === 3 ? (
            <>
              <Select
                labelId="meat-value-label"
                id="meat-value"
                value={meatValue}
                onChange={handleMeatValueChange}
                label="부위"
              >
                <MenuItem value="등심">등심</MenuItem>
                <MenuItem value="설도">설도</MenuItem>
              </Select>
              <Select
                labelId="seqno-label"
                id="seqno-value"
                value={seqnoValue}
                onChange={handleSeqnoValueChange}
                label="회차 정보"
              >
                <MenuItem value="1">1회차</MenuItem>
                <MenuItem value="2">2회차</MenuItem>
                <MenuItem value="3">3회차</MenuItem>
                <MenuItem value="4">4회차</MenuItem>
              </Select>
            </>
          ) : (
            <div>
              <Select
                labelId="meat-state-label"
                id="meat-state"
                value={meatState}
                onChange={handleMeatStateChange}
                label="육류 가공 상태"
              >
                <MenuItem value="원육">원육</MenuItem>
                <MenuItem value="처리육">처리육</MenuItem>
                <MenuItem value="가열육">가열육</MenuItem>
              </Select>
              <Select
                labelId="animal-label"
                id="animal"
                value={animalType}
                onChange={handleAnimalChange}
                label="동물 종류"
              >
                <MenuItem value="소">소</MenuItem>
                <MenuItem value="돼지">돼지</MenuItem>
              </Select>
              <Select
                labelId="grade-label"
                id="grade"
                value={grade}
                onChange={handleGradeChange}
                label="등급"
              >
                <MenuItem value="5">전체</MenuItem>
                {animalType === '소' && <MenuItem value="0">1++</MenuItem>}
                {animalType === '소' && <MenuItem value="1">1+</MenuItem>}
                {animalType === '소' && <MenuItem value="2">1</MenuItem>}
                {animalType === '소' && <MenuItem value="3">2</MenuItem>}
                {animalType === '소' && <MenuItem value="4">3</MenuItem>}
              </Select>
            </div>
          )}
        </Box>
      </Box>

      {/* BoxPlot(통계) */}
      <CustomTabPanel value={value} index={0}>
        <BoxPlotChart
          key={`sens-${startDate}-${endDate}-${animalType}-${grade}-${meatState}`}
          meatState={meatState}
          dataType="sensory"
          startDate={startDate}
          endDate={endDate}
          animalType={animalType}
          grade={grade}
        />
        {meatState !== '가열육' && (
          <BoxPlotChart
            key={`taste-${startDate}-${endDate}-${animalType}-${grade}-${meatState}`}
            meatState={meatState}
            dataType="taste"
            startDate={startDate}
            endDate={endDate}
            animalType={animalType}
            grade={grade}
          />
        )}
      </CustomTabPanel>

      {/* HeatMap(분포) */}
      <CustomTabPanel value={value} index={1}>
        <HeatMapChart
          key={`sens-${startDate}-${endDate}-${animalType}-${grade}-${meatState}`}
          meatState={meatState}
          dataType="sensory"
          startDate={startDate}
          endDate={endDate}
          animalType={animalType}
          grade={grade}
        />
        {meatState !== '가열육' && (
          <HeatMapChart
            key={`taste-${startDate}-${endDate}-${animalType}-${grade}-${meatState}`}
            meatState={meatState}
            dataType="taste"
            startDate={startDate}
            endDate={endDate}
            animalType={animalType}
            grade={grade}
          />
        )}
      </CustomTabPanel>

      <CustomTabPanel value={value} index={2}>
        <CorrelationChart
          key={`sens-${startDate}-${endDate}-${animalType}-${grade}-${meatState}`}
          meatState={meatState}
          dataType="sensory"
          startDate={startDate}
          endDate={endDate}
          animalType={animalType}
          grade={grade}
        />
        {meatState !== '가열육' && (
          <CorrelationChart
            key={`taste-${startDate}-${endDate}-${animalType}-${grade}-${meatState}`}
            meatState={meatState}
            dataType="taste"
            startDate={startDate}
            endDate={endDate}
            animalType={animalType}
            grade={grade}
          />
        )}
      </CustomTabPanel>

      <CustomTabPanel value={value} index={3}>
        <TasteTime
          startDate={startDate}
          endDate={endDate}
          seqnoValue={seqnoValue}
          meatValue={meatValue}
        />
      </CustomTabPanel>
    </Box>
  );
};

export default StatsTabs;
