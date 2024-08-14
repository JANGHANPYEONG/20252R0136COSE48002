// import react
import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
// import mui
import {
  Button,
  Box,
  Card,
  Popover,
  Divider,
  Typography,
  IconButton,
} from '@mui/material';
// import react-icons
import { FaArrowRotateLeft, FaFilter } from 'react-icons/fa6';
// import date-picker
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DemoContainer } from '@mui/x-date-pickers/internals/demo';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs from 'dayjs';

import updateDates from './helper/updateDates';
import style from './style/searchfilterbarstyle';
const navy = '#0F3659';

const SearchFilterBar = ({ setStartDate, setEndDate }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);

  //조회 기간 (탭으로 클릭 시)
  const [isDur, setIsDur] = useState(true);
  const [duration, setDuration] = useState(
    searchParams.get('duration') || 'week'
  );
  const [durStart, setDurStart] = useState(null);
  const [durEnd, setDurEnd] = useState(null);
  // 조회 기간 (직접 입력할 시)
  const [calenderStart, setCalenderStart] = useState(
    dayjs(searchParams.get('start') || null)
  );
  const [calenderEnd, setCalenderEnd] = useState(
    dayjs(searchParams.get('end') || null)
  );

  const [initialDuration, setInitialDuration] = useState(duration);
  const [initialCalenderStart, setInitialCalenderStart] =
    useState(calenderStart);
  const [initialCalenderEnd, setInitialCalenderEnd] = useState(calenderEnd);
  const [initialIsDur, setInitialIsDur] = useState(isDur);

  // console.log(duration);

  // 탭으로 클릭시 조회기간 변경
  const handleDr = (event) => {
    setDuration(event.target.value);
    // 직접입력을 null로 바꾸기 (초기화)
    setCalenderStart(null);
    setCalenderEnd(null);
    setIsDur(true);
  };

  //완료 버튼 클릭하면 변함
  const handleCompleteBtn = () => {
    const queryParams = new URLSearchParams();
    if (!isDur) {
      //직접 입력할 시
      if (calenderStart) {
        const startVal = `${calenderStart.$y}-${String(calenderStart.$M + 1).padStart(2, '0')}-${String(calenderStart.$D).padStart(2, '0')}T00:00:00`;
        setStartDate(startVal);
        queryParams.set('start', calenderStart.format('YYYY-MM-DD'));
      }
      if (calenderEnd) {
        const endVal = `${calenderEnd.$y}-${String(calenderEnd.$M + 1).padStart(2, '0')}-${String(calenderEnd.$D).padStart(2, '0')}T23:59:59`;
        setEndDate(endVal);
        queryParams.set('end', calenderEnd.format('YYYY-MM-DD'));
      }
      setDuration(null);
    } else {
      //탭으로 클릭할시
      queryParams.set('duration', duration);
      const { start, end } = updateDates(duration);
      setStartDate(start);
      setEndDate(end);
    }
    setInitialDuration(duration);
    setInitialCalenderStart(calenderStart);
    setInitialCalenderEnd(calenderEnd);
    setInitialIsDur(isDur);
    navigate(`${location.pathname}?${queryParams.toString()}`);
  };

  const handleReset = () => {
    setDuration('week');
    setCalenderStart(null);
    setCalenderEnd(null);
    setIsDur(true);

    const { start, end } = updateDates('week');
    setStartDate(start);
    setEndDate(end);

    const queryParams = new URLSearchParams();
    queryParams.set('duration', 'week');
    navigate(`${location.pathname}?${queryParams.toString()}`);
  };

  // pop over 결정
  const [anchorEl, setAnchorEl] = useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
    setDuration(initialDuration);
    setCalenderStart(initialCalenderStart);
    setCalenderEnd(initialCalenderEnd);
    setIsDur(initialIsDur);
  };

  const open = Boolean(anchorEl);
  const id = open ? 'simple-popover' : undefined;

  return (
    <div>
      <Button
        variant="contained"
        onClick={handleClick}
        style={{
          backgroundColor: navy,
          height: '35px',
          borderRadius: '10px',
          width: 'fit-content',
          fontSize: '15px',
          textTransform: 'none',
        }}
      >
        <FaFilter style={{ marginRight: '4px' }} />
        Filter
      </Button>
      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
      >
        <Card style={style.cardStyle}>
          <Box
            id=""
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              margin: '0px 20px',
            }}
          >
            <Typography>조회기간</Typography>
            {duration === 'week' ? (
              <Button variant="contained" value="week" style={style.button}>
                1주
              </Button>
            ) : (
              <Button
                variant="outlined"
                value="week"
                style={style.unClickedbutton}
                onClick={handleDr}
              >
                1주
              </Button>
            )}
            {duration === 'month' ? (
              <Button variant="contained" value="month" style={style.button}>
                1개월
              </Button>
            ) : (
              <Button
                variant="outlined"
                value="month"
                style={style.unClickedbutton}
                onClick={handleDr}
              >
                1개월
              </Button>
            )}
            {duration === 'quarter' ? (
              <Button variant="contained" value="quarter" style={style.button}>
                1분기
              </Button>
            ) : (
              <Button
                variant="outlined"
                value="quarter"
                style={style.unClickedbutton}
                onClick={handleDr}
              >
                1분기
              </Button>
            )}
            {duration === 'year' ? (
              <Button variant="contained" value="year" style={style.button}>
                1년
              </Button>
            ) : (
              <Button
                variant="outlined"
                value="year"
                style={style.unClickedbutton}
                onClick={handleDr}
              >
                1년
              </Button>
            )}
            {duration === 'total' ? (
              <Button variant="contained" value="total" style={style.button}>
                전체
              </Button>
            ) : (
              <Button
                variant="outlined"
                value="total"
                style={style.unClickedbutton}
                onClick={handleDr}
              >
                전체
              </Button>
            )}
          </Box>
          <Box style={{ display: 'flex' }}>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DemoContainer components={['DatePicker']} sx={{ mx: 'auto' }}>
                <div style={{ display: 'flex', marginLeft: '20px' }}>
                  <DatePicker
                    disableFuture
                    onChange={(newVal) => {
                      setCalenderStart(newVal);
                      setIsDur(false);
                    }}
                    value={isDur ? null : calenderStart}
                    label="시작날짜"
                    slotProps={{ textField: { size: 'small' } }}
                    format={'YYYY-MM-DD'}
                  />
                  ~
                  <DatePicker
                    disableFuture
                    minDate={
                      calenderStart ? calenderStart : dayjs('1970-01-01')
                    }
                    onChange={(newVal) => {
                      setCalenderEnd(newVal);
                      setIsDur(false);
                    }}
                    value={isDur ? null : calenderEnd}
                    label="종료날짜"
                    slotProps={{ textField: { size: 'small' } }}
                    format={'YYYY-MM-DD'}
                  />
                </div>
              </DemoContainer>
            </LocalizationProvider>
          </Box>

          <Divider variant="middle" style={{ margin: '10px 0px' }} />

          <Box style={{ display: 'flex', justifyContent: 'end' }}>
            <button
              onClick={() => {
                setIsDur(false);
                handleCompleteBtn();
                setAnchorEl(null);
              }}
              style={style.finishBtn}
            >
              완료
            </button>
          </Box>
        </Card>
      </Popover>

      <IconButton
        style={{
          border: `1px solid ${navy}`,
          borderRadius: '10px',
          width: '35px',
          height: '35px',
          marginLeft: '10px',
          padding: '0px',
        }}
        size="small"
        onClick={handleReset}
      >
        <FaArrowRotateLeft />
      </IconButton>
    </div>
  );
};

export default SearchFilterBar;
