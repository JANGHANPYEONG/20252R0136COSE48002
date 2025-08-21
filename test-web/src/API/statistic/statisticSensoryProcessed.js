import { apiIP } from '../../config';

export const statisticSensoryProcessed = async (
  startDate,
  endDate,
  animal_type,
  grade
) => {
  const url = `http://${apiIP}/statistic/sensory-stats/processed?start=${startDate}&end=${endDate}&animal_type=${animal_type}&grade=${grade}`;
  const response = await fetch(url);
  return response;
};

export default statisticSensoryProcessed;
