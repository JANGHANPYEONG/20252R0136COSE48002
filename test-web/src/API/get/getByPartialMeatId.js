import { apiIP } from '../../config';

export const getByPartialMeatId = async (
  partialMeatId,
  offset,
  count,
  startDate,
  endDate,
  specieValue
) => {
  const response = await fetch(
    `http://${apiIP}/meat/get/by-partial-id?meatId=${partialMeatId}&offset=${offset}&count=${count}&start=${startDate}&end=${endDate}&specieValue=${specieValue}`
  );

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  return response.json();
};
export default getByPartialMeatId;
