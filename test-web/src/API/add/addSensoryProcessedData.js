import { apiIP } from '../../config';

// 처리육 수정 POST API
export const addSensoryProcessedData = async (
  processedInput, // 처리육 데이터 (수정값)
  i, // 처리육 seqno
  meatId, // 이력번호
  userId,
  isPost
) => {
  const dataSet = {
    ['marbling']: parseFloat(processedInput.marbling),
    ['color']: parseFloat(processedInput.color),
    ['texture']: parseFloat(processedInput.texture),
    ['surfaceMoisture']: parseFloat(processedInput.surfaceMoisture),
    ['overall']: parseFloat(processedInput.overall),
  };

  //request body에 보낼 데이터 전처리
  let req = {
    ['sensoryData']: dataSet,
  };
  req = {
    ...req,
    ['meatId']: meatId,
    ['userId']: userId,
    ['seqno']: i + 1,
    ['imgAdded']: false,
    ['filmedAt']: '2024-07-08T12:12:12',
  };
  if (!isPost) delete req['userId'];

  ///meat/add/sensory-eval로 처리육 데이터 생성/수정 API 전송
  try {
    const response = await fetch(`http://${apiIP}/meat/add/sensory-eval`, {
      method: `${isPost ? 'POST' : 'PATCH'}`,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req),
    });
    if (!response.ok) {
      throw new Error(
        'sensory_eval 서버에서 응답 코드가 성공(2xx)이 아닙니다.'
      );
    }
    // 서버에서 받은 JSON 응답 데이터를 parse
    const responseData = await response.json();
    return { ...responseData, ok: true };
  } catch (err) {
    console.log('error');
    console.error(err);
  }
};
export default addSensoryProcessedData;
