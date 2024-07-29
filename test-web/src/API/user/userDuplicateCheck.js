import { apiIP } from "../../config";

export const userDuplicateCheck = async(userId) =>{
    const response = await fetch(
        `http://${apiIP}/user/duplicate-check?userId=${userId}`
      );
      return response
}