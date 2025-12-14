import { apiIP } from '../../config';

export const statisticTime = async (startDate, endDate, seqnoValue, meat_value) => {
  const response = await fetch(
    `http://${apiIP}/statistic/time?start=${startDate}&end=${endDate}&seqno=${seqnoValue}&meat_value=${meat_value}`
  );

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  return response;
};
export default statisticTime;
