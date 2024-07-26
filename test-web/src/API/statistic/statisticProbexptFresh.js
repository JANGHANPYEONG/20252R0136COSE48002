import { apiIP } from '../../config';

export const statisticProbexptFresh = async (
  startDate,
  endDate,
  animalType,
  grade
) => {
  const response = await fetch(
    `http://${apiIP}/meat/statistic/probexpt-stats/fresh?start=${startDate}&end=${endDate}&animalType=${animalType}&grade=${grade}`
  );
  return response;
};
