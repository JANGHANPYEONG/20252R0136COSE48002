import { useState } from 'react';
import { Backdrop, Box, Modal, Fade, Button, Typography } from '@mui/material';

const navy = '#0F3659';

// 처리육 데이터 수정 전, 이미지 먼저 업로드 필수 알림 경고창
export default function InputTransitionsModal({ setModal }) {
  //화면 창 닫기
  const [open, setOpen] = useState(true);
  const handleClose = () => {
    setOpen(false);
    setModal(false);
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
            <Typography id="transition-modal-title" variant="h6" component="h2">
              <span
                style={{ color: navy, fontSize: '20px', fontWeight: '600' }}
              >
                이미지를 먼저 업로드해야 합니다.
              </span>
            </Typography>
            <div
              style={{
                display: 'flex',
                width: '100%',
                justifyContent: 'center',
                marginTop: '20px',
              }}
            >
              <Button
                variant="contained"
                sx={{ marginRight: '5px', backgroundColor: navy }}
                onClick={handleClose}
              >
                닫기
              </Button>
            </div>
          </Box>
        </Fade>
      </Modal>
    </div>
  );
}

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 500,
  height: '160px',
  bgcolor: 'background.paper',
  //border: '2px solid #000',
  boxShadow: 24,
  p: 4,
  borderRadius: '10px',
};
