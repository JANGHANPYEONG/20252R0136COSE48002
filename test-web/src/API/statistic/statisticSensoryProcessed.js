import { apiIP } from '../../config';

export const statisticSensoryProcessed = async (
  startDate,
  endDate,
  animalType,
  grade,
  meatValue
) => {
  const url = `http://${apiIP}/meat/statistic/sensory-stats/processed?start=${startDate}&end=${endDate}&animalType=${animalType}&grade=${grade}` + (meatValue && meatValue !== '전체' ? `&meatValue=${meatValue}` : '');
  const response = await fetch(url);
  return response;
};

export default statisticSensoryProcessed;
