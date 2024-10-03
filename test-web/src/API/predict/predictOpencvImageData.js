import { apiIP } from '../../config';

// 가열육 수정 POST API
export const predictOpencvImageData = async (
  meatId, // 이력번호
  seqno,
  isPost
) => {
  try {
    const response = await fetch(
      `http://${apiIP}/meat/predict/process-opencv?meatId=${meatId}&seqno=${seqno}`,
      {
        method: `${isPost ? 'POST' : 'PATCH'}`,
        headers: {
          'Content-Type': 'application/json',
        },
        // body: JSON.stringify(req),
      }
    );

    if (!response.ok) {
      throw new Error('opencv image processing request failed');
    }
  } catch (error) {
    console.error('Error during prediction:', error);
  }
};
export default predictOpencvImageData;
