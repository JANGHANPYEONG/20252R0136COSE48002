import { apiIP } from '../../config';

export const statisticSensoryFresh = async (startDate, endDate, animalType, grade) => {
  const url = `http://${apiIP}/statistic/sensory-stats/fresh?start=${startDate}&end=${endDate}&animal_type=${animalType}&grade=${grade}`;
  const response = await fetch(url);
  return response;
};

export default statisticSensoryFresh;
