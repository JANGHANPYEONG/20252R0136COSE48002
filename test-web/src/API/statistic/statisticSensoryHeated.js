import { apiIP } from '../../config';

export const statisticSensoryHeated = async (
  startDate,
  endDate,
  animalType,
  grade
) => {
  const response = await fetch(
    `http://${apiIP}/meat/statistic/sensory-stats/heated-fresh?start=${startDate}&end=${endDate}&animalType=${animalType}&grade=${grade}`
  );
  return response;
};

export default statisticSensoryHeated;
