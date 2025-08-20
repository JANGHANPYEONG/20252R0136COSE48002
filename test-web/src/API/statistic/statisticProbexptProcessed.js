import { apiIP } from '../../config';

export const statisticProbexptProcessed = async (
  startDate,
  endDate,
  animalType,
  grade,
  meatValue
) => {
  const url = `http://${apiIP}/meat/statistic/probexpt-stats/processed?start=${startDate}&end=${endDate}&animalType=${animalType}&grade=${grade}` + (meatValue && meatValue !== '전체' ? `&meatValue=${meatValue}` : '');
  const response = await fetch(url);
  return response;
};

export default statisticProbexptProcessed;
