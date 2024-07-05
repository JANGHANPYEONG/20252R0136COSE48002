import { useState, useEffect, useRef } from 'react';
// react-bootstrap
import { Card } from 'react-bootstrap';
// icons
import { FaArrowLeft, FaArrowRight, FaUpload } from 'react-icons/fa';
// mui
import { IconButton } from '@mui/material';
// 이미지 수정 api 호출
import updateRawData from '../../../API/update/updateRawData';
import updateProcessedData from '../../../API/update/updateProcessedData';
import uploadNewImgToFirebase from '../../../API/firebase/uploadNewImgToFirebase';

import { TIME_ZONE } from '../../../config';
import { computePeriod } from '../computePeriod';

const navy = '#0F3659';

const MeatImgsCard = ({
  edited, //수정버튼 클릭 여부
  page, // 페이지 종류
  raw_img_path, // 원육 이미지 경로
  processed_img_path, // 처리육 이미지 경로
  setIsUploadingDone, // 이미지 업로드 처리 완료 setState 함수
  id, // 이력번호
  raw_data, // 원육 데이터
  setIsLimitedToChangeImage, // 이미지 수정 실패 여부 setState 함수
  butcheryYmd, // 도축 일자
  processedInput, // 처리육 데이터
  processed_data, // 처리육 데이터
  processedMinute, // 처리 시간 (분)
}) => {
  // 1.이미지 배열 만들기
  const [imgArr, setImgArr] = useState([raw_img_path]);
  useEffect(() => {
    processed_img_path.length !== 0
      ? //{}이 아닌 경우
        setImgArr([...imgArr, ...processed_img_path])
      : //{}인 경우 -> 1회차 처리육 정보 입력을 위해 null 생성
        setImgArr([...imgArr, null]);
  }, []);

  // 이미지 배열 페이지네이션
  const [currentIdx, setCurrIdx] = useState(0);

  // 1) 이미지 페이지네이션 '>' 버튼 클릭
  const handleNextClick = () => {
    setCurrIdx((prev) => (prev + 1) % imgArr.length);
  };

  // 2) 이미지 페이지네이션 '<' 버튼 클릭
  const handlePrevClick = () => {
    setCurrIdx((prev) => (prev - 1) % imgArr.length);
  };

  // 3)이미지 페이지네이션 특정 숫자 클릭
  const handleNumClick = (e) => {
    setCurrIdx(e.target.outerText - 1);
  };

  // 2.이미지 파일 변경
  const fileRef = useRef(null);
  // 이미지 미리보기 or 이미지 변경 될 때 마다 firebase 업로드
  const [isImgChanged, setIsImgChanged] = useState(false);

  /**
   * 이미지 파일 업로드 한 경우
   * 1. firebase의 fire storage에 이미지 업로드
   * 2.1 원육 이미지를 수정한 경우, 원육 수정 API 호출
   * 2.2 처리육 이미지를 수정한 경우, 처리육 수정 API 호출
   */
  const handleImgChange = (newImgFile) => {
    if (newImgFile) {
      const fileName = id + '-' + currentIdx + '.png';
      const folderName = 'sensory_evals';
      const reader = new FileReader();
      //로그인한 유저 정보
      const userId = JSON.parse(localStorage.getItem('UserInfo'))['userId'];
      // 수정 시간
      const createdDate = new Date(new Date().getTime() + TIME_ZONE)
        .toISOString()
        .slice(0, -5);
      // period 계산
      const elapsedHour = computePeriod(butcheryYmd);
      // 파일에서 이미지 선택
      reader.onload = async () => {
        //업로드 중 메세지를 띄우기 위한 변수
        setIsUploadingDone(false);
        // firebase에 업로드
        await uploadNewImgToFirebase(
          newImgFile,
          folderName,
          fileName,
          setIsUploadingDone
        );

        // 원육 이미지 수정 api 호출 currentIdx == 0
        if (currentIdx === 0) {
          const response = updateRawData(
            raw_data,
            id,
            userId,
            createdDate,
            elapsedHour
          );
          response.then((response) => {
            if (response.statusText === 'NOT FOUND') {
              setIsLimitedToChangeImage(true); //실패시
            } else {
              updatePreviews(reader); //성공시
              setIsImgChanged(true);
            }
            setIsUploadingDone(true); // 업로드 중 화면 중지
          });
          // 실패 시
          console.log('limit to change', response.statusText);
        } else {
          // 처리육 수정 api 호출 이미지인 경우 0이상
          const i = currentIdx - 1;
          await updateProcessedData(
            processedInput[i],
            processed_data[i],
            processedMinute[i],
            i,
            id,
            userId,
            createdDate,
            elapsedHour
          )
            // 수정 성공 시
            .then((response) => {
              console.log('처리육 이미지 수정 POST요청 성공:', response);
              updatePreviews(reader);
              setIsImgChanged(true);
            })
            // 수정 실패 시
            .catch((error) => {
              console.error('처리육 이미지 수정 POST 요청 오류:', error);
              setIsLimitedToChangeImage(true); //실패시
            });
          setIsUploadingDone(true); // 업로드 중 화면 중지
        }
      };
      reader.readAsDataURL(newImgFile);
    }
  };

  // 이미지 수정시, 수정 API 호출까지 성공한 경우, 업로드 한 이미지로 미리보기 수정
  const updatePreviews = (reader) => {
    let newImages = imgArr;
    newImages[currentIdx] = reader.result;
    setImgArr(newImages);
  };

  return (
    <Card style={{ width: '27vw', margin: '0px 10px', boxShadow: 24 }}>
      {/* 1.1. 이미지 */}
      <Card.Body>
        {/**이미지 제목 */}
        <Card.Text style={style.imgTitleContainer}>
          {
            // 이미지 제목
            currentIdx === 0 ? (
              <div style={style.imgTitleWrapper}>원육이미지</div>
            ) : (
              <div style={style.imgTitleWrapper}>
                딥에이징 {currentIdx}회차 이미지
              </div>
            )
          }
          <div style={{ display: 'flex' }}>
            {
              /**
               * page 가 수정및조회인 경우,
               * 이미지 파일을 업로드하기 위한 <input type="file"/>
               */
              page === '수정및조회' && (
                <div>
                  <input
                    className="form-control"
                    id="formFile"
                    accept="image/jpg,impge/png,image/jpeg,image/gif"
                    type="file"
                    ref={fileRef}
                    onChange={(e) => {
                      handleImgChange(e.target.files[0]);
                    }}
                    style={{ marginRight: '20px', display: 'none' }}
                  />
                  {
                    /**
                     * 수정 버튼 클릭시 이미지 조회 버튼 생성
                     */
                    edited && (
                      <IconButton
                        type="button"
                        className="btn btn-success"
                        style={style.imgUploadWrapper}
                        onClick={() => {
                          fileRef.current.click();
                        }}
                      >
                        <span style={style.imgUploadTextWrapper}>
                          이미지 업로드
                        </span>
                        <FaUpload />
                      </IconButton>
                    )
                  }
                </div>
              )
            }
          </div>
        </Card.Text>
        {/**이미지 */}
        <Card.Text>
          <div style={style.imgContainer}>
            {
              // 실제 이미지
              imgArr[currentIdx] ? (
                isImgChanged === true ? (
                  /*이미지 미리 보기*/
                  <img
                    ng-src="data:image/jpeg;base64,{{image}}"
                    src={imgArr[currentIdx]}
                    alt={`Image ${currentIdx + 1}`}
                    style={style.imgWrapper}
                  />
                ) : (
                  <img
                    ng-src="data:image/jpeg;base64,{{image}}"
                    src={imgArr[currentIdx] + '?time=' + new Date()}
                    alt={`Image ${currentIdx + 1}`}
                    style={style.imgWrapper}
                  />
                )
              ) : (
                <div style={style.imgNotExistWrapper}>
                  이미지가 존재하지 않습니다.
                </div>
              )
            }
          </div>
        </Card.Text>
        {/**페이지네이션 */}
        <Card.Text style={style.paginationBtnWrapper}>
          <IconButton
            variant="contained"
            size="small"
            sx={style.paginationLeftBtn}
            onClick={handlePrevClick}
            disabled={currentIdx === 0}
          >
            <FaArrowLeft />
          </IconButton>
          <div style={style.paginationNavBtnWrapper}>
            {
              // 페이지네이션
              Array.from({ length: imgArr.length }, (_, idx) => (
                <div
                  value={idx}
                  style={
                    currentIdx === idx
                      ? style.paginationNavCurrDiv
                      : style.paginationNavNotCurrDiv
                  }
                  onClick={(e) => handleNumClick(e)}
                >
                  {idx + 1}
                </div>
              ))
            }
          </div>
          <IconButton
            variant="contained"
            size="small"
            sx={style.paginationRightBtn}
            onClick={handleNextClick}
            disabled={currentIdx === imgArr.length - 1}
          >
            <FaArrowRight />
          </IconButton>
        </Card.Text>
      </Card.Body>
    </Card>
  );
};

export default MeatImgsCard;

const style = {
  imgTitleContainer: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  imgTitleWrapper: {
    color: '#002984',
    height: '40px',
    fontSize: '18px',
    fontWeight: '800',
  },
  imgContainer: {
    height: '350px',
    width: '100%',
    borderRadius: '10px',
  },
  imgWrapper: {
    height: '350px',
    width: '400px',
    objectFit: 'contain',
  },
  imgNotExistWrapper: {
    height: '350px',
    width: '400px',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
  imgUploadWrapper: {
    height: '40px',
    width: '160px',
    border: `1px solid ${navy}`,
    borderRadius: '5px',
  },
  imgUploadTextWrapper: {
    color: `${navy}`,
    fontSize: '16px',
    marginRight: '5px',
  },
  paginationBtnWrapper: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
  paginationLeftBtn: {
    height: '35px',
    width: '35px',
    borderRadius: '10px',
    padding: '0',
    border: '1px solid black',
  },
  paginationNavBtnWrapper: {
    display: 'flex',
    justifyContent: 'center',
    margin: '0px 5px',
  },
  paginationNavCurrDiv: {
    height: 'fit-content',
    width: 'fit-content',
    padding: '10px',
    borderRadius: '5px',
    color: navy,
  },
  paginationNavNotCurrDiv: {
    height: '100%',
    width: 'fit-content',
    borderRadius: '5px',
    padding: '10px',
    color: '#b0bec5',
  },
  paginationRightBtn: {
    height: '35px',
    width: '35px',
    borderRadius: '10px',
    padding: '0',
    border: '1px solid black',
  },
};
