import { apiIP } from '../../config';

export const userRegister = async (req) => {
  req = { ...req, alarm: true };
  console.log(req);
  const registrationResponse = await fetch(`http://${apiIP}/user/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(req),
  });
  return registrationResponse;
};

export default userRegister;
