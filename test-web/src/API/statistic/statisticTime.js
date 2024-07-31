import { apiIP } from '../../config';

export const statisticTime = async (startDate, endDate, meatValue) => {
  const response = await fetch(
    `http://${apiIP}/meat/statistic/time?start=${startDate}&end=${endDate}&meatValue=${meatValue}`
  );

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  return response;
};
