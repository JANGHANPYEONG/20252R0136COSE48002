// import timezone
import { TIME_ZONE } from '../config';

const updateDates = (duration) => {
  const s = new Date();
  if (duration === 'week') {
    s.setDate(s.getDate() - 7);
  } else if (duration === 'month') {
    s.setMonth(s.getMonth() - 1);
  } else if (duration === 'quarter') {
    s.setMonth(s.getMonth() - 3);
  } else if (duration === 'year') {
    s.setFullYear(s.getFullYear() - 1);
  } else if (duration === 'total') {
    s.setFullYear(1970);
    s.setMonth(0);
    s.setDate(1);
    s.setHours(0, 0, 0, 0);
  }
  const start = new Date(s.getTime() + TIME_ZONE).toISOString().slice(0, -5);
  const end = new Date(new Date().getTime() + TIME_ZONE)
    .toISOString()
    .slice(0, -5);

  return { start, end };
};

export default updateDates;
