import { apiIP } from '../../config';

export const deleteDeepAging = async (meatId, seqno) => {
  const response = await fetch(
    `http://${apiIP}/meat/delete/deep-aging?meatId=${meatId}&seqno=${seqno}`,
    {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );
  return response;
};

export default deleteDeepAging;
