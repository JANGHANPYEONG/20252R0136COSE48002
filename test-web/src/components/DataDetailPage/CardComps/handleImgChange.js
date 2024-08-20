import { computePeriod } from '../computeTime';
import addSensoryRawImg from '../../../API/add/addSensoryRawImg';
import addSensoryProcessedData from '../../../API/add/addSensoryProcessedData';
import uploadNewImgToFirebase from '../../../API/firebase/uploadNewImgToFirebase';
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
  processedMinute,
  butcheryYmd,
}) => {
  if (newImgFile) {
    const fileName = id + '-' + currentIdx + '.png';
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
          }
          setIsUploadingDone(true);
        });
      } else {
        const i = currentIdx - 1;
        await addSensoryProcessedData(
          processedInput[i],
          processed_data[i],
          processedMinute[i],
          i,
          id,
          userId,
          createdDate,
          elapsedHour
        )
          .then((response) => {
            updatePreviews(reader);
            setIsImgChanged(true);
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
