import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import PropTypes from 'prop-types';
import { Tabs, Tab, Box, Button, useTheme } from '@mui/material';
import * as React from 'react';
import { Select, MenuItem } from '@mui/material';
import Sens_FreshMeat from './Charts/BoxPlot/Sens_FreshMeat';
import Sens_ProcMeat from './Charts/BoxPlot/Sens_ProcMeat';
import Sens_HeatedMeat from './Charts/BoxPlot/Sens_HeatedMeat';
import Taste_FreshMeat from './Charts/BoxPlot/Taste_FreshMeat';
import Taste_ProcMeat from './Charts/BoxPlot/Taste_ProcMeat';
import Sens_Fresh_Map from './Charts/HeatMap/Sens_Fresh_Map';
import Sens_Heated_Map from './Charts/HeatMap/Sens_Heated_Map';
import Taste_Fresh_Map from './Charts/HeatMap/Taste_Fresh_Map';
import Taste_Proc_Map from './Charts/HeatMap/Taste_Proc_Map';
import Taste_Time from './Charts/Time/Taste_Time';
import Sens_Proc_Map from './Charts/HeatMap/Sens_Proc_Map';
import Taste_Fresh_Corr from './Charts/Corr/Taste_Fresh_Corr';
import Sense_Proc_Corr from './Charts/Corr/Sens_Proc_Corr';
import Sense_Heated_Corr from './Charts/Corr/Sens_Heated_Corr';
import Sense_Fresh_Corr from './Charts/Corr/Sens_Fresh_Corr';
import Taste_Proc_Corr from './Charts/Corr/Taste_Proc_Corr';

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
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);

  const [value, setValue] = useState(0);
  const [slot, setSlot] = useState('week');
  const [alignment, setAlignment] = useState('맛');
  //const [gradeAlignment, setGradeAlignment] = useState('소');
  const [secondary, setSecondary] = useState('원육');
  const [animalType, setAnimalType] = useState('소');
  const [grade, setGrade] = useState('5');
  const [meatValue, setMeatValue] = useState('등심');
  const [seqnoValue, setSeqnoValue] = useState(1);

  useEffect(() => {
    // console.log('stat tab' + startDate, '-', endDate);
  }, [startDate, endDate]);
  const theme = useTheme();
  const handleChange = (event, newValue) => {
    setValue(newValue);
  };
  const handleMeatValueChange = (event) => {
    setMeatValue(event.target.value);
  };
  const handleSeqnoValueChange = (event) => {
    setSeqnoValue(event.target.value);
  };
  const handleFirstChange = (event) => {
    setAlignment(event.target.value);
    setSecondary('원육'); // Initialize secondary to "원육"
  };

  const handleSecondChange = (event) => {
    setSecondary(event.target.value);
  };

  const handleAnimalChange = (event) => {
    setAnimalType(event.target.value);
    setGrade('5'); // Reset the grade to 'all' when the animal type changes
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
          {value == 3 ? (
            <>
              <Select
                labelId="meat-value-label"
                id="meat-value"
                value={meatValue}
                onChange={handleMeatValueChange}
                //label="원육, 처리육, 가열육"
              >
                <MenuItem value="등심">등심</MenuItem>
                <MenuItem value="설도">설도</MenuItem>
              </Select>
              <Select
                labelId="seqno-label"
                id="seqno-value"
                value={seqnoValue}
                onChange={handleSeqnoValueChange}
                //label="원육, 처리육, 가열육"
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
                labelId="secondary-label"
                id="secondary"
                value={secondary}
                onChange={handleSecondChange}
                label="원육, 처리육, 가열육"
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
        {secondary === '원육' ? (
          <>
            <Sens_FreshMeat
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            <Taste_FreshMeat
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
          </>
        ) : secondary === '처리육' ? (
          <>
            <Sens_ProcMeat
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            <Taste_ProcMeat
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
          </>
        ) : secondary === '가열육' ? (
          <>
            <Sens_HeatedMeat
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            {/* 가열육에 대한 맛 컴포넌트가 없다면 다음 줄을 제거하거나 다른 적절한 컴포넌트로 대체하세요 */}
            {/* <Taste_FreshMeat
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
        {secondary === '원육' ? (
          <>
            <Sens_Fresh_Map
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            <Taste_Fresh_Map
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
          </>
        ) : secondary === '처리육' ? (
          <>
            <Sens_Proc_Map
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            <Taste_Proc_Map
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
          </>
        ) : secondary === '가열육' ? (
          <>
            <Sens_Heated_Map
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            {/* 가열육에 대한 맛 컴포넌트가 없다면 다음 줄을 제거하거나 다른 적절한 컴포넌트로 대체하세요 */}
            {/* <Taste_FreshMeat
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
        {secondary === '원육' ? (
          <>
            <div style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
              <Sense_Fresh_Corr
                key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
                startDate={startDate}
                endDate={endDate}
                animalType={animalType}
                grade={grade}
              />
            </div>
            <div style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
              <Taste_Fresh_Corr
                key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
                startDate={startDate}
                endDate={endDate}
                animalType={animalType}
                grade={grade}
              />
            </div>
          </>
        ) : secondary === '처리육' ? (
          <>
            <Sense_Proc_Corr
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            <Taste_Proc_Corr
              key={`taste-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
          </>
        ) : secondary === '가열육' ? (
          <>
            <Sense_Heated_Corr
              key={`sens-${startDate}-${endDate}-${animalType}-${grade}`}
              startDate={startDate}
              endDate={endDate}
              animalType={animalType}
              grade={grade}
            />
            {/* 가열육에 대한 맛 컴포넌트가 없다면 다음 줄을 제거하거나 다른 적절한 컴포넌트로 대체하세요 */}
            {/* <Taste_FreshMeat
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
        <Taste_Time
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
