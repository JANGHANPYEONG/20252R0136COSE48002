import { apiIP } from '../../config';

export const userList = async () => {
  const usersListResponse = await fetch(`http://${apiIP}/user`);
  return usersListResponse;
};
