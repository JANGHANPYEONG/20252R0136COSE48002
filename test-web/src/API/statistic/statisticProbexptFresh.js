import { apiIP } from '../../config';

export const statisticProbexptFresh = async (
  startDate,
  endDate,
  animalType,
  grade,
  meatValue
) => {
  const url = `http://${apiIP}/statistic/probexpt-stats/fresh?start=${startDate}&end=${endDate}&animal_type=${animalType}&grade=${grade}`;
  const response = await fetch(url);
  return response;
};
export default statisticProbexptFresh;
