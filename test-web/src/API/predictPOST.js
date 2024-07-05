import { apiIP } from '../config';

function PredictData(elapsedHour, len, id) {
  //로그인한 유저 정보
  const userId = JSON.parse(localStorage.getItem('UserInfo'))['userId'];

  for (let i = 0; i < len; i++) {
    let req = {
      ['id']: id,
      ['seqno']: i,
      ['userId']: userId,
      ['period']: Math.round(elapsedHour),
    };

    const res = JSON.stringify(req);
    try {
      fetch(`http://${apiIP}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: res,
      });
      console.log(res);
    } catch (err) {
      console.log('error');
      console.error(err);
    }
  }
}

export default PredictData;
