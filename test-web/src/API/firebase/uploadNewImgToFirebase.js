// firebase
import { ref as storageRef, uploadBytes } from 'firebase/storage';
import { storage } from '../../firebase-config.js';

// firebase 이미지 업로드
export const uploadNewImgToFirebase = async (
  file,
  folderName,
  fileName,
  SetisUploadedToFirebase
) => {
  const fileRef = storageRef(storage, `${folderName}/${fileName}`);
  try {
    // 2. 변경할 이미지 firebase storage에 올리기
    await uploadBytes(fileRef, file);
    //firebase 업로드 성공 시
    console.log('File uploaded successfully!', fileName);
  } catch (error) {
    //firebase 업로드 실패 시
    console.error('Error uploading file:', error, fileName);
  }
};

export default uploadNewImgToFirebase;