import { apiIP } from '../../config';

export const userDelete = async (userId) => {
  const response = await fetch(`http://${apiIP}/user/delete?userId=${userId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response;
};
