import { apiIP } from "../../config";

// 실험실 데이터 수정 POST API
export default async function updateProbexptData(
  data, // 실험실 데이터
  i, // 실험실 seqno
  id, // 이력번호
  createdDate, // 생성 날짜
  userId, // 로그인한 사용자 id
  elapsedHour // 경과 시간
) {
  //request body에 보낼 데이터 전처리
  let req = {
    ...data,
  };
  req = {
    ...req,
    ["id"]: id,
    ["updatedAt"]: createdDate,
    ["userId"]: userId,
    ["seqno"]: i,
    ["period"]: Math.round(elapsedHour),
  };
  // /meat/add/probexpt-data로 실험 수정 데이터 전송
  try {
    const response = await fetch(`http://${apiIP}/meat/add/probexpt-data`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(req),
    });
    if (!response.ok) {
      throw new Error(
        "probexpt_data 서버에서 응답 코드가 성공(2xx)이 아닙니다."
      );
    }
    // 서버에서 받은 JSON 응답 데이터를 해석
    const responseData = await response.json();
    return responseData;
  } catch (err) {
    console.log("error");
    console.error(err);
  }
}
