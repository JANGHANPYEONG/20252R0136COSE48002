import { apiIP } from '../../config';

export const statisticProbexptProcessed = async (
  startDate,
  endDate,
  animalType,
  grade,
  meatValue
) => {
  const url = `http://${apiIP}/statistic/probexbt-stats/processed?start=${startDate}&end=${endDate}&animal_type=${animalType}&grade=${grade}`;
  const response = await fetch(url);
  return response;
};

export default statisticProbexptProcessed;
