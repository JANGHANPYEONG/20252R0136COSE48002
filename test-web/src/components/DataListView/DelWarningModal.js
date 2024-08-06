import { useState } from 'react';
import { Backdrop, Box, Modal, Fade, Button, Typography } from '@mui/material';
import { FaRegTrashAlt } from 'react-icons/fa';
import { deleteMeat } from '../../API/delete/deleteMeat';
const navy = '#0F3659';

// 삭제 경고창 컴포넌트
const DelWarningModal = ({
  idArr, //삭제할 id 배열
  setIsDelClick, // 삭제 버튼 클릭 setState 함수
  pageOffset, // 현재 페이지 offset
  startDate, // 조회 시작 날짜
  endDate, // 조회 종료 날짜
}) => {
  //화면 창 닫기
  const [open, setOpen] = useState(true);
  const handleClose = () => {
    setOpen(false);
    setIsDelClick(false);
  };

  // 삭제 API 호출함수

  // 삭제 후 reload 시 쿼리 파라미터 변수 값
  const params = [
    `pageOffset=${pageOffset}`,
    `startDate=${startDate}`,
    `endDate=${endDate}`,
  ];

  // 삭제 버튼 클릭 시
  const handleOnDelete = async () => {
    await deleteMeat({ id: idArr });
    // 삭체 후 새로고침
    window.location.href =
      'http://' +
      window.location.host +
      window.location.pathname +
      '?' +
      params.join('&');
    // 모달 창 닫기
    handleClose();
  };
  return (
    <div>
      <Modal
        aria-labelledby="transition-modal-title"
        aria-describedby="transition-modal-description"
        open={open}
        onClose={handleClose}
        closeAfterTransition
        slots={{ backdrop: Backdrop }}
        slotProps={{
          backdrop: {
            timeout: 500,
          },
        }}
      >
        <Fade in={open}>
          <Box sx={style}>
            <Typography
              id="transition-modal-title"
              key={'transition-modal-title'}
              variant="h6"
              component="h2"
            >
              <span
                style={{ color: navy, fontSize: '20px', fontWeight: '600' }}
              >
                정말로 삭제하시겠습니까?
              </span>
              <div></div>
              <span
                style={{
                  color: '#b0bec5',
                  fontSize: '12px',
                  lineHeight: '5px',
                }}
              >
                삭제 버튼 클릭 시 아래 관리 번호에 해당하는 데이터가 바로
                삭제됩니다. 삭제된 데이터는 복원할 수 없습니다.
              </span>
            </Typography>

            <Box
              style={{
                border: '1px solid #b0bec5',
                borderRadius: '10px',
                margin: '10px 0px',
                height: '130px',
                padding: '0px 10px',
              }}
            >
              {idArr.map((id) => (
                <Typography
                  id="transition-modal-description"
                  key={'transition-modal-description'}
                  sx={{ mt: 2 }}
                >
                  {id}
                </Typography>
              ))}
            </Box>

            <div
              style={{ display: 'flex', width: '100%', justifyContent: 'end' }}
            >
              <Button
                variant="outlined"
                sx={{ marginRight: '5px' }}
                onClick={handleClose}
                style={{
                  backgroundColor: 'white',
                  marginRight: '10px',
                  border: `1px solid ${navy}`,
                  height: '35px',
                  borderRadius: '10px',
                  width: '100px',
                  fontSize: '17px',
                }}
              >
                아니오
              </Button>
              <Button
                variant="contained"
                onClick={handleOnDelete}
                style={{
                  backgroundColor: navy,
                  height: '35px',
                  borderRadius: '10px',
                  width: '100px',
                  fontSize: '17px',
                }}
              >
                <FaRegTrashAlt />
                삭제
              </Button>
            </div>
          </Box>
        </Fade>
      </Modal>
    </div>
  );
};

export default DelWarningModal;

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 500,
  bgcolor: 'background.paper',
  boxShadow: 24,
  p: 4,
  borderRadius: '10px',
};
