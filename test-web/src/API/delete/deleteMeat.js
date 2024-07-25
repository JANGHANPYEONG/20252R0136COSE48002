import { apiIP } from "../../config";

export const deleteMeat = async (req) => {
    await fetch(`http://${apiIP}/meat/delete/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req),
    });
  };