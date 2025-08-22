import { apiIP } from '../config';

// 승인 (confirm)
export const confirmMeat = async (meatId, setStateChanged) => {
  try {
    const response = await fetch(`http://${apiIP}/meat/confirm`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ meatid: meatId }),
    });
    setStateChanged?.(true);
    if (!response.ok) {
      throw new Error('서버에서 응답 코드가 성공(2xx)이 아닙니다.');
    }
    return await response.json();
  } catch (err) {
    console.error(err);
  }
};

// 반려 (reject)
export const rejectMeat = async (meatId, setStateChanged) => {
  try {
    const response = await fetch(`http://${apiIP}/meat/reject`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ meatid: meatId }),
    });
    setStateChanged?.(true);
    if (!response.ok) {
      throw new Error('서버에서 응답 코드가 성공(2xx)이 아닙니다.');
    }
    return await response.json();
  } catch (err) {
    console.error(err);
  }
};
