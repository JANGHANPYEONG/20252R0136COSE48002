import { apiIP } from '../../config';

export const statisticSensoryProcessed = async (
  startDate,
  endDate,
  animalType,
  grade
) => {
  const response = await fetch(
    `http://${apiIP}/meat/statistic/sensory-stats/processed?start=${startDate}&end=${endDate}&animalType=${animalType}&grade=${grade}`
  );
  return response;
};
