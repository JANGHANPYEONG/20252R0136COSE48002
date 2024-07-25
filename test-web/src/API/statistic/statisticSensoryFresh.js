import { apiIP } from '../../config';

export const statisticSensoryFresh = async (
  startDate,
  endDate,
  animalType,
  grade
) => {
  const response = await fetch(
    `http://${apiIP}/meat/statistic/sensory-stats/fresh?start=${startDate}&end=${endDate}&animalType=${animalType}&grade=${grade}`
  );
  return response;
};
