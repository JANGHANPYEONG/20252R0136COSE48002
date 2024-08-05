import { apiIP } from '../../config';

// 원육 수정 POST API (이미지 수정)
export const addSensoryRawImg = async (
  raw_data, // 원육 데이터
  id, // 이력번호
  userId, // 로그인한 사용자 id
  createdDate, // 생성 시간
  elapsedHour // 경과 시간
) => {
  //request body에 보낼 데이터 전처리
  let req = {
    ...raw_data,
  };
  req = {
    ...req,
    ['id']: id,
    ['createdAt']: createdDate,
    ['userId']: userId,
    ['seqno']: 0,
    ['period']: Math.round(elapsedHour),
  };

  // /meat/add/sensory-eval로 원육 수정 데이터 API 전송
  try {
    const response = await fetch(`http://${apiIP}/meat/add/sensory-eval`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req),
    });
    return response;
  } catch (err) {
    console.log('error');
    console.error(err);
  }
};
export default addSensoryRawImg;
