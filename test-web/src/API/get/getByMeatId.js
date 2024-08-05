import { apiIP } from '../../config';

export const getByMeatId = async (meatId) => {
  const response = await fetch(
    `http://${apiIP}/meat/get/by-meat-id?meatId=${meatId}`
  );

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }
  return response;
};

export default getByMeatId;
