import { apiIP } from '../../config';

export const statisticProbexptProcessed = async (
  startDate,
  endDate,
  animalType,
  grade
) => {
  const response = await fetch(
    `http://${apiIP}/meat/statistic/probexpt-stats/processed?start=${startDate}&end=${endDate}&animalType=${animalType}&grade=${grade}`
  );
  return response
};
