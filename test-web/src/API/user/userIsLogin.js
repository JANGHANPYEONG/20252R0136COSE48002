import { apiIP } from '../../config';

export const userIsLogin = async (loginEmail) => {
    const response = await fetch(
        `http://${apiIP}/user/login?userId=${loginEmail}`
      );
      return response;
};
