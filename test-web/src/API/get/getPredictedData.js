import { apiIP } from '../../config';

export const getPredictedData = async (meatId, seqno) => {
  try {
    const response = await fetch(
      `http://${apiIP}/meat/get/predict-data?meatId=${meatId}&seqno=${seqno}`
    );
    if (!response.ok) {
      throw new Error('Network response was not ok', meatId, '-', seqno);
    }
    const json = await response.json();
    return json;
  } catch (error) {
    console.error('Error fetching data seqno ', seqno, ':', error);
    return null;
  }
};

export default getPredictedData;
