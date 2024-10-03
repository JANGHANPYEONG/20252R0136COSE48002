import { apiIP } from '../../config';

export const predictSensoryData = async (meatId, seqno) => {
  try {
    // let req = {
    //   ['meatId']: meatId,
    //   ['seqno']: parseInt(processedToggleValue),
    // };
    const response = await fetch(
      `http://${apiIP}/meat/predict/sensory-eval?meatId=${meatId}&seqno=${seqno}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // body: JSON.stringify(req),
      }
    );

    if (!response.ok) {
      throw new Error('Prediction request failed');
    }
  } catch (error) {
    console.error('Error during prediction:', error);
  }
};

export default predictSensoryData;
