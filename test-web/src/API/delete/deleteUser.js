import { apiIP } from "../../config";

export const deleteMeat = async (userId) => {
    const response = await fetch(
        `http://${apiIP}/user/delete?userId=${userId}`,
        {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );


}