import { apiIP } from '../../config';

export const predictOpencvTrainingData = async (meatId, seqno) => {
  try {
    // let req = {
    //   ['meatId']: meatId,
    //   ['seqno']: parseInt(processedToggleValue),
    // };
    const response = await fetch(
      `http://${apiIP}/meat/predict/process-opencv-training?meatId=${meatId}&seqno=${seqno}`,
      {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        // body: JSON.stringify(req),
      }
    );

    if (!response.ok) {
      throw new Error('opencv training data processing request failed');
    }
  } catch (error) {
    console.error('Error during prediction:', error);
  }
};

export default predictOpencvTrainingData;
