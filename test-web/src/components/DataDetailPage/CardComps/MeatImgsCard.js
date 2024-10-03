import { useState, useEffect, useRef } from 'react';
// react-bootstrap
import { Card, OverlayTrigger } from 'react-bootstrap';
// icons
import { FaArrowLeft, FaArrowRight, FaUpload } from 'react-icons/fa';
// mui
import { IconButton } from '@mui/material';
// UserContext
import { useUser } from '../../../Utils/UserContext';

import handleImgChange from './handleImgChange';
import style from '../style/meatimgscardstyle';
import { Tooltip } from '@mui/material';
import useOpencvImageData from '../../../API/get/getOpencvImageDataSWR';
import OpencvImgMaker from './OpencvImgMaker';

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
  processed_data_seq, // 회차 정보
  isPost,
}) => {
  // 1.이미지 배열 만들기
  const [imgArr, setImgArr] = useState([raw_img_path]);
  useEffect(() => {
    setImgArr([...imgArr, ...processed_img_path]);
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

  // UserContext에서 유저 정보 불러오기
  const user = useUser();

  // 이미지 수정시, 수정 API 호출까지 성공한 경우, 업로드 한 이미지로 미리보기 수정
  const updatePreviews = (reader) => {
    let newImages = imgArr;
    newImages[currentIdx] = reader.result;
    setImgArr(newImages);
  };

  // 툴팁 이미지 데이터
  const [tooltipImgData, setTooltipImgData] = useState([]);
  const { data, isLoading, isError } = useOpencvImageData(id, currentIdx);

  const handleFileChange = (e) => {
    handleImgChange({
      newImgFile: e.target.files[0],
      currentIdx,
      imgArr,
      id,
      setIsUploadingDone,
      setIsLimitedToChangeImage,
      setIsImgChanged,
      updatePreviews,
      userId: user.userId,
      raw_data,
      processedInput,
      processed_data,
      processed_data_seq,
      processedMinute,
      butcheryYmd,
      isPost,
      data,
    });
  };

  //데이터 전처리
  useEffect(() => {
    if (data !== null && data !== undefined) {
      setTooltipImgData(data);
    }
  }, [data]);

  return (
    <Card
      style={{
        width: '27vw',
        margin: '0px 10px',
        boxShadow: 24,
        minWidth: '360px',
        height: '65vh',
        minHeight: '500px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* 1.1. 이미지 */}
      <Card.Body style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/**이미지 제목 */}
        <Card.Text style={style.imgTitleContainer}>
          {
            // 이미지 제목
            currentIdx === 0 ? (
              <div style={style.imgTitleWrapper}>원육이미지</div>
            ) : (
              <div style={style.imgTitleWrapper}>
                딥에이징 {processed_data_seq[currentIdx]}차 이미지
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
                    onChange={handleFileChange}
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
          <OverlayTrigger
            placement="right"
            delay={{ show: 250, hide: 400 }}
            overlay={
              <Tooltip id="button-tooltip">
                {' '}
                {isLoading ? (
                  <div style={style.overlayNotExistWrapper}>Loading...</div>
                ) : isError || !data || data.msg ? (
                  // 데이터가 없는 경우
                  <div style={style.overlayNotExistWrapper}>
                    단면, 컬러팔레트 이미지가 없습니다
                  </div>
                ) : data.segmentImage &&
                  data.fatColorPalette &&
                  data.proteinColorPalette &&
                  data.totalColorPalette ? (
                  // 올바른 데이터인지 검사
                  data.fatColorPalette.every(
                    (color) =>
                      color[0] === 0 && color[1] === 0 && color[2] === 0
                  ) ? (
                    // 컬러가 모두 0인 경우
                    <div style={style.overlayNotExistWrapper}>
                      올바르지 않은 데이터입니다
                    </div>
                  ) : (
                    // 데이터가 있는 경우
                    <OpencvImgMaker data={tooltipImgData} />
                  )
                ) : (
                  // 그 외
                  <div style={style.overlayNotExistWrapper}>
                    오류로 인해 단면, 컬러팔레트 이미지를 불러올 수 없습니다
                  </div>
                )}
              </Tooltip>
            }
          >
            <div style={style.imgContainer}>
              {
                // 실제 이미지
                imgArr[currentIdx] ? (
                  isImgChanged === true ? (
                    /*이미지 미리 보기*/
                    <img
                      src={imgArr[currentIdx]}
                      alt={`Image ${currentIdx + 1}`}
                      style={style.imgWrapper}
                    />
                  ) : (
                    <img
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
          </OverlayTrigger>
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
