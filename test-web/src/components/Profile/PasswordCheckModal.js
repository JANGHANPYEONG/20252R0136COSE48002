import React, { useState } from 'react';
import Modal from '@mui/material/Modal';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import {
  getAuth,
  EmailAuthProvider,
  reauthenticateWithCredential,
} from 'firebase/auth';

const navy = '#0F3659';

const PasswordCheckModal = ({ isOpen, onClose, onSuccess }) => {
  const [password, setPassword] = useState('');

  const handlePasswordChange = (e) => {
    setPassword(e.target.value);
  };

  const reauthenticate = async () => {
    const auth = getAuth();
    const user = auth.currentUser;
    const credential = EmailAuthProvider.credential(user.email, password);

    try {
      await reauthenticateWithCredential(user, credential);
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error reauthenticating:', error);
      // Here you might want to show an error message to the user
    }
  };

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
          component="div"
          style={{
            color: '#0F3659',
            fontSize: '22px',
            fontWeight: '600',
          }}
        >
          비밀번호 확인
        </Typography>
        <TextField
          label="비밀번호"
          type="password"
          value={password}
          onChange={handlePasswordChange}
          sx={{ mt: 2, mb: 2 }}
          fullWidth
        />
        <Button
          variant="contained"
          onClick={reauthenticate}
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

export default PasswordCheckModal;
