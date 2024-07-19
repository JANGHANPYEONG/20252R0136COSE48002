import { apiIP } from '../../config';

// 가열육 수정 POST API
export default async function updateHeatedData(
  data, // 가열육 데이터
  i, // 가열육 seqno
  meatId, // 이력번호
  createdDate, // 생성 날짜
  userId, // 로그인한 사용자 id
  elapsedHour // 경과 시간
) {
  const dataset = {
    ['flavor']: parseFloat(data.flavor),
    ['juiciness']: parseFloat(data.juiciness),
    ['tenderness']: parseFloat(data.tenderness),
    ['umami']: parseFloat(data.umami),
    ['palatability']: parseFloat(data.palatability),
  };
  //console.log("data",data)
  //request body에 보낼 데이터 가공
  let req = {
    heatedmeatSensoryData: dataset,
  };
  req = {
    ...req,
    ['meatId']: meatId,
    //["createdAt"]: createdDate,
    //["userId"]: userId,
    ['seqno']: i,
    //["period"]: Math.round(elapsedHour),
    //['filmedAt']: '2024-07-07 12:12:12',
    ['imgAdded']: false,
  };
  console.log('req:', req, 'meatId:',meatId);

  //meat/add/heatedmeat-eval로 수정 API 전송
  try {
    const response = await fetch(`http://${apiIP}/meat/add/heatedmeat-eval`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req),
    });
    if (!response.ok) {
      throw new Error(
        'heatedmeat_eval 서버에서 응답 코드가 성공(2xx)이 아닙니다.'
      );
    }
    // 서버에서 받은 JSON 응답 데이터를 해석
    const responseData = await response.json();
    return responseData;
  } catch (err) {
    console.log('error');
    console.error(err);
  }
}
