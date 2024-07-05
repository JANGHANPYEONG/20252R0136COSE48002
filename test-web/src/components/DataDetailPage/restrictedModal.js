import { useState } from 'react';
import { Backdrop, Box, Modal, Fade, Button, Typography } from '@mui/material';

const navy = '#0F3659';

// 이미지 수정 API 전송 실패 모달창
export default function RestrictedModal({ setIsLimitedToChangeImage }) {
  //화면 창 닫기
  const [open, setOpen] = useState(true);
  const handleClose = () => {
    setOpen(false);
    setIsLimitedToChangeImage(false);
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
                이미지를 수정할 수 없습니다.
              </span>
              <div></div>
              <span
                style={{
                  color: '#b0bec5',
                  fontSize: '12px',
                  lineHeight: '5px',
                }}
              >
                서버를 확인하거나 이미지 수정 권한이 있는지 확인하십시오.
              </span>
            </Typography>

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
  bgcolor: 'background.paper',
  boxShadow: 24,
  p: 4,
  borderRadius: '10px',
};
