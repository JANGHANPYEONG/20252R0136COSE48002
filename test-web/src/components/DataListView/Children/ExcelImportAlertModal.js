import { useState } from 'react';
import { Backdrop, Box, Modal, Fade, Button, Typography } from '@mui/material';
import style from '../style/excelimportalertmodalstyle';

const navy = '#0F3659';

//엑셀 파일 업로드 실패/ 성공 여부 모달창
const ExcelImportAlertModal = ({
  isImportSuccessed,
  setAlertDone,
  setIsImportSuccessed,
}) => {
  //화면 창 닫기
  const [open, setOpen] = useState(true);
  const handleClose = () => {
    setAlertDone(false);
    setIsImportSuccessed(true);
    setOpen(false);
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
              {isImportSuccessed ? (
                <span
                  style={{ color: navy, fontSize: '20px', fontWeight: '600' }}
                >
                  엑셀 파일 업로드에 성공하였습니다.
                </span>
              ) : (
                <span
                  style={{ color: navy, fontSize: '20px', fontWeight: '600' }}
                >
                  엑셀 파일 업로드에 실패하였습니다.
                </span>
              )}
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
};

export default ExcelImportAlertModal;
