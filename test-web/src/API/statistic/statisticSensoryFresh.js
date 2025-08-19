import { apiIP } from '../../config';

export const statisticSensoryFresh = async (startDate, endDate, animalType, grade, meatValue) => {
  const url = `http://${apiIP}/meat/statistic/sensory-stats/fresh?start=${startDate}&end=${endDate}&animalType=${animalType}&grade=${grade}` + (meatValue && meatValue !== '전체' ? `&meatValue=${meatValue}` : '');
  const response = await fetch(url);
  return response;
};

export default statisticSensoryFresh;
