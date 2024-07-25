import { apiIP } from "../../config";

// 원육 수정 POST API (이미지 수정)
export default async function updateRawImg(
  raw_data, // 원육 데이터
  id, // 이력번호
  userId, // 로그인한 사용자 id
  createdDate, // 생성 시간
  elapsedHour // 경과 시간
) {
  //request body에 보낼 데이터 전처리
  let req = {
    ...raw_data,
  };
  req = {
    ...req,
    ["id"]: id,
    ["createdAt"]: createdDate,
    ["userId"]: userId,
    ["seqno"]: 0,
    ["period"]: Math.round(elapsedHour),
  };

  // /meat/add/sensory-eval로 원육 수정 데이터 API 전송
  try {
    const response = await fetch(`http://${apiIP}/meat/add/sensory-eval`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(req),
    });
    /*if (!response.ok) {
            throw new Error('sensory_eval 서버에서 응답 코드가 성공(2xx)이 아닙니다.');
        }
        */
    return response;
  } catch (err) {
    console.log("error");
    console.error(err);
  }
}
