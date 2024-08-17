import { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Tabs, Tab, Box } from '@mui/material';
import { Select, MenuItem } from '@mui/material';
import SensFreshMeat from './Charts/BoxPlot/SensFreshMeat';
import SensProcMeat from './Charts/BoxPlot/SensProcMeat';
import SensHeatedMeat from './Charts/BoxPlot/SensHeatedMeat';
import TasteFreshMeat from './Charts/BoxPlot/TasteFreshMeat';
import TasteProcMeat from './Charts/BoxPlot/TasteProcMeat';
import SensFreshMap from './Charts/HeatMap/SensFreshMap';
import SensHeatedMap from './Charts/HeatMap/SensHeatedMap';
import TasteFreshMap from './Charts/HeatMap/TasteFreshMap';
import TasteProcMap from './Charts/HeatMap/TasteProcMap';
import TasteTime from './Charts/Time/TasteTime';
import SensProcMap from './Charts/HeatMap/SensProcMap';
import TasteFreshCorr from './Charts/Corr/TasteFreshCorr';
import SenseProcCorr from './Charts/Corr/SensProcCorr';
import SenseHeatedCorr from './Charts/Corr/SensHeatedCorr';
import SenseFreshCorr from './Charts/Corr/SensFreshCorr';
import TasteProcCorr from './Charts/Corr/TasteProcCorr';

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
        {meatState === '원육' ? (
          <>
            <SensFreshMeat
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            <TasteFreshMeat
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
          </>
        ) : meatState === '처리육' ? (
          <>
            <SensProcMeat
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            <TasteProcMeat
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
          </>
        ) : meatState === '가열육' ? (
          <>
            <SensHeatedMeat
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            {/* 가열육에 대한 맛 컴포넌트가 없다면 다음 줄을 제거하거나 다른 적절한 컴포넌트로 대체하세요 */}
            {/* <TasteFreshMeat
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            /> */}
          </>
        ) : null}
      </CustomTabPanel>

      {/* HeatMap(분포) */}
      <CustomTabPanel value={value} index={1}>
        {meatState === '원육' ? (
          <>
            <SensFreshMap
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            <TasteFreshMap
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
          </>
        ) : meatState === '처리육' ? (
          <>
            <SensProcMap
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            <TasteProcMap
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
          </>
        ) : meatState === '가열육' ? (
          <>
            <SensHeatedMap
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            {/* 가열육에 대한 맛 컴포넌트가 없다면 다음 줄을 제거하거나 다른 적절한 컴포넌트로 대체하세요 */}
            {/* <TasteFreshMeat
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            /> */}
          </>
        ) : null}
      </CustomTabPanel>

      <CustomTabPanel value={value} index={2}>
        {meatState === '원육' ? (
          <>
            <div style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
              <SenseFreshCorr
                key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
                startDate={startDate}
                endDate={endDate}
                animalType={animalType}
                grade={grade}
              />
            </div>
            <div style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
              <TasteFreshCorr
                key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
                startDate={startDate}
                endDate={endDate}
                animalType={animalType}
                grade={grade}
              />
            </div>
          </>
        ) : meatState === '처리육' ? (
          <>
            <SenseProcCorr
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            <TasteProcCorr
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
          </>
        ) : meatState === '가열육' ? (
          <>
            <SenseHeatedCorr
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            {/* 가열육에 대한 맛 컴포넌트가 없다면 다음 줄을 제거하거나 다른 적절한 컴포넌트로 대체하세요 */}
            {/* <TasteFreshMeat
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            /> */}
          </>
        ) : null}
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
