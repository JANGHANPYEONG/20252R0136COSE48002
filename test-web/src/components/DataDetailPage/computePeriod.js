// import timezone
import { TIME_ZONE } from '../../config';

// 경과 시간 계산
function computePeriod(butcheryYmd) {
  // 수정 시간
  const createdDate = new Date(new Date().getTime() + TIME_ZONE)
    .toISOString()
    .slice(0, -5);
  // period 계산
  const year = butcheryYmd.slice(0, 4);
  const month = butcheryYmd.slice(4, 6);
  const day = butcheryYmd.slice(6);
  const butcheryDate = new Date(year, month, day, 0, 0, 0);
  const [date, time] = createdDate.split('T');
  const [yy, mm, dd] = date.split('-');
  const [h, m, s] = time.split(':');
  const createdDate2 = new Date(yy, mm, dd, h, m, s);
  const elapsedMSec = createdDate2.getTime() - butcheryDate.getTime();
  const elapsedHour = elapsedMSec / 1000 / 60 / 60;
  return elapsedHour;
}

//현재 날짜 계산
function computeCurrentDate() {
  const createdDate = new Date(new Date().getTime() + TIME_ZONE)
    .toISOString()
    .slice(0, -5);
  const [date, time] = createdDate.split('T');
  const [yy, mm, dd] = date.split('-');

  return [yy, mm, dd];
}

export { computePeriod, computeCurrentDate };
