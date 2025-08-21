import { apiIP } from '../../config';

export const statisticSensoryHeated = async (
  startDate,
  endDate,
  animal_type,
  grade
) => {
  const url = `http://${apiIP}/statistic/sensory-stats/heated-fresh?start=${startDate}&end=${endDate}&animal_type=${animal_type}&grade=${grade}`;
  const response = await fetch(url);
  return response;
};

export default statisticSensoryHeated;