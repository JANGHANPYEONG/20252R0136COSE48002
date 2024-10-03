import { computePeriod } from '../computeTime';
import addSensoryRawImg from '../../../API/add/addSensoryRawImg';
import addSensoryProcessedData from '../../../API/add/addSensoryProcessedData';
import uploadNewImgToFirebase from '../../../API/firebase/uploadNewImgToFirebase';
import predictOpencvImageData from '../../../API/predict/predictOpencvImageData';
import { TIME_ZONE } from '../../../config';

const handleImgChange = async ({
  newImgFile,
  currentIdx,
  imgArr,
  id,
  setIsUploadingDone,
  setIsLimitedToChangeImage,
  setIsImgChanged,
  updatePreviews,
  userId,
  raw_data,
  processedInput,
  processed_data,
  processed_data_seq,
  processedMinute,
  butcheryYmd,
  isPost,
  data,
}) => {
  if (newImgFile) {
    const existSeq = processed_data_seq
      .filter((item) => item.includes('회')) // '회'가 포함된 항목만 필터링
      .map((item) => parseInt(item.replace('회', '')));

    const fileName = id + '-' + existSeq[currentIdx - 1] + '.png';
    const folderName = 'sensory_evals';
    const reader = new FileReader();
    const createdDate = new Date(new Date().getTime() + TIME_ZONE)
      .toISOString()
      .slice(0, -5);
    const elapsedHour = computePeriod(butcheryYmd);

    reader.onload = async () => {
      setIsUploadingDone(false);
      await uploadNewImgToFirebase(
        newImgFile,
        folderName,
        fileName,
        setIsUploadingDone
      );

      if (currentIdx === 0) {
        const response = addSensoryRawImg(raw_data, id, userId);

        response.then((response) => {
          if (response.statusText === 'NOT FOUND') {
            setIsLimitedToChangeImage(true);
          } else {
            updatePreviews(reader);
            setIsImgChanged(true);
            // 원육 이미지는 항상 수정이므로 PATCH로 OpenCV 데이터 처리
            predictOpencvImageData(id, 0, false);
          }
          setIsUploadingDone(true);
        });
      } else {
        const i = currentIdx - 1;
        const response = addSensoryProcessedData(
          processedInput[i],
          existSeq[i],
          id,
          userId,
          isPost,
          true
        );
        response
          .then((response) => {
            updatePreviews(reader);
            setIsImgChanged(true);
            // OpenCV 데이터가 없으면 POST로, 있으면 PATCH로 처리
            if (!data || data.msg) {
              isPost = true;
            }
            // 처리육은 isPost 값에 따라 생성/수정 구분하여 OpenCV 데이터 처리
            predictOpencvImageData(id, existSeq[i], isPost);
          })
          .catch((error) => {
            console.error('처리육 이미지 수정 POST 요청 오류:', error);
            setIsLimitedToChangeImage(true);
          });
        setIsUploadingDone(true);
      }
    };

    reader.readAsDataURL(newImgFile);
  }
};

export default handleImgChange;
