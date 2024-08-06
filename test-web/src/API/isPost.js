export const isPost = async (
  data, // 기존 데이터
  input, // 새로운 Input 데이터
  isPosted = false // 같은 세션에서 POST로 등록된 데이터인지 여부 -> 액셀 import 시에는 기본값 false
) => {
  const newInput = input.map((value) => {
    if (value === '') return undefined;
    else if (value === null) return null;
    else if (value !== undefined) return Number(value);
    else return value;
  });
  const isDataExists = !data.every((value) => value === undefined);
  const isInputExists = !newInput.every(
    (value) => value === undefined || value === null
  );

  let isSame;
  if (!isDataExists) {
    if (isPosted) {
      return false;
    } // 새로 POST되었던 Input이 다시 null로 변경되어 들어올 경우 PATCH로 모든 값을 null로 변경
    isSame = !isInputExists;
  } else {
    isSame = newInput.every((value, idx) => value === data[idx]);
  }

  if (isSame) return undefined;
  else if (!isDataExists && !isSame) return true;
  else return false;
};

export default isPost;
