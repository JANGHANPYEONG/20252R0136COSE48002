import { useState, useEffect } from 'react';
// react-bootstrap
import { Card } from 'react-bootstrap';
// icons
import { FaArrowLeft, FaArrowRight } from 'react-icons/fa';
// mui
import { IconButton } from '@mui/material';

const navy = '#0F3659';

const MeatImgsCardStatic = ({
  raw_img_path, // 원육 이미지 경로
  processed_img_path, // 처리육 이미지 경로
}) => {
  //이미지 배열 만들기
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
        </Card.Text>
        {/**이미지 */}
        <Card.Text>
          <div style={style.imgContainer}>
            {
              // 실제 이미지
              imgArr[currentIdx] ? (
                <img
                  ng-src="data:image/jpeg;base64,{{image}}"
                  src={imgArr[currentIdx] + '?time=' + new Date()}
                  alt={`Image ${currentIdx + 1}`}
                  style={style.imgWrapper}
                />
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

export default MeatImgsCardStatic;

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

