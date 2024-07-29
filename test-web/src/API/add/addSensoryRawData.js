import { apiIP } from '../../config';
import { computeCurrentDate } from '../../components/DataDetailPage/computePeriod';
export default async function addSensoryRawData(rawInput, i, meatId) {
  const [yy, mm, dd] = computeCurrentDate();
  const dataSet = {
    marbling: parseFloat(rawInput.marbling),
    color: parseFloat(rawInput.color),
    texture: parseFloat(rawInput.texture),
    surfaceMoisture: parseFloat(rawInput.surfaceMoisture),
    overall: parseFloat(rawInput.overall),
  };

  let req = {
    ['meatId']: meatId,
    ['seqno']: i,
    ['imgAdded']: false,
    ['filmedAt']: '2024-07-08T12:12:12',
    ['sensoryData']: dataSet,
  };

  try {
    const response = await fetch(`http://${apiIP}/meat/add/sensory-eval`, {
      method: 'PATCH',
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
    return responseData;
  } catch (err) {
    console.log('error');
    console.error(err);
  }
}
