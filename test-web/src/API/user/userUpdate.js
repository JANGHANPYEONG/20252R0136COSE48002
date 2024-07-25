import { apiIP } from '../../config';

export const userUpdate = async (req) => {
  const response = await fetch(`http://${apiIP}/user/update`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  });
  return response;
};
