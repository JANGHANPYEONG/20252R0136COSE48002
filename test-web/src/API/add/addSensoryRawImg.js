import { apiIP } from '../../config';

// 원육 수정 PATCH API (이미지 수정)
export const addSensoryRawImg = async (
  raw_data, // 원육 데이터
  id, // 이력번호
  userId // 로그인한 사용자 id
) => {
  const sensoryData = {
    marbling: raw_data.marbling,
    color: raw_data.color,
    texture: raw_data.texture,
    surfaceMoisture: raw_data.surfaceMoisture,
    overall: raw_data.overall,
  };
  //request body에 보낼 데이터 전처리
  const req = {
    sensoryData: sensoryData,
    ['meatId']: id,
    ['userId']: userId,
    ['seqno']: 0,
    ['imgAdded']: true,
    ['filmedAt']: raw_data.filmedAt,
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
