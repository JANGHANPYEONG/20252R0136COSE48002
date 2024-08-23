import React from 'react';
import Modal from '@mui/material/Modal';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';

const navy = '#0F3659';

const SelfDeleteConfirmationModal = ({ isOpen, onClose, onConfirm }) => {
  return (
    <Modal open={isOpen} onClose={onClose}>
      <Box
        sx={{
          position: 'absolute',
          width: 300,
          backgroundColor: 'white',
          borderRadius: 8,
          boxShadow: 5,
          p: 2,
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
        }}
      >
        <Typography
          variant="h6"
          style={{
            color: '#0F3659',
            fontSize: '22px',
            fontWeight: '600',
          }}
        >
          회원 탈퇴 확인
        </Typography>
        <Typography
          style={{
            fontSize: '18px',
            fontWeight: '550',
            marginTop: '1rem',
            marginBottom: '0.5rem',
          }}
        >
          정말 탈퇴하시겠습니까? <br />이 작업은 취소할 수 없습니다.
        </Typography>
        <Button
          variant="contained"
          onClick={onConfirm}
          style={{ backgroundColor: navy, margin: '0.5rem' }}
        >
          확인
        </Button>
        <Button
          variant="contained"
          onClick={onClose}
          style={{
            backgroundColor: 'grey',
            color: 'white',
            margin: '0.5rem',
          }}
        >
          취소
        </Button>
      </Box>
    </Modal>
  );
};

export default SelfDeleteConfirmationModal;
