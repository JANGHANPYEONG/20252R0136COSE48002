import React, { useState } from 'react';
import Typography from '@mui/material/Typography';
import { useNavigate } from 'react-router-dom';
import CustomSnackbar from '../components/Base/CustomSnackbar';
import { userDelete } from '../API/user/userDelete';
import ProfileEditForm from '../components/Profile/ProfileEditForm';
import PasswordCheckModal from '../components/Profile/PasswordCheckModal';
import SelfDeleteConfirmationModal from '../components/Profile/SelfDeleteConfirmationModal';
import { useUser, useSetUser } from '../Utils/UserContext';

const Profile = () => {
  const user = useUser();
  const setUser = useSetUser();
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  const navigate = useNavigate();

  const handleSnackbarShow = (message, severity) => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleUpdate = (updatedData) => {
    setUser(updatedData);
    // window.dispatchEvent(new Event('userInfoUpdated'));
    handleSnackbarShow('회원정보가 수정되었습니다.', 'success');
  };

  const handleDeleteRequest = () => {
    setIsPasswordModalOpen(true);
  };

  const handlePasswordSuccess = () => {
    setIsConfirmModalOpen(true);
  };

  const deleteSelf = async () => {
    try {
      const response = await userDelete(user.userId);

      if (response.ok) {
        setUser({}); // 사용자 정보 초기화
        localStorage.setItem('isLoggedIn', 'false');
        navigate('/');
        window.location.reload();
      }
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  };

  return (
    <div style={{ paddingTop: '100px', minHeight: '0px' }}>
      <Typography
        variant="h4"
        gutterBottom
        style={{
          marginBottom: '20px',
          color: '#0F3659',
          fontSize: '30px',
          fontWeight: '600',
        }}
      >
        Profile
      </Typography>

      <ProfileEditForm
        userInfo={user}
        onUpdate={handleUpdate}
        onDeleteRequest={handleDeleteRequest}
        handleSnackbarShow={handleSnackbarShow}
      />

      <PasswordCheckModal
        isOpen={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
        onSuccess={handlePasswordSuccess}
      />

      <SelfDeleteConfirmationModal
        isOpen={isConfirmModalOpen}
        onClose={() => setIsConfirmModalOpen(false)}
        onConfirm={deleteSelf}
      />

      <CustomSnackbar
        open={snackbarOpen}
        message={snackbarMessage}
        severity={snackbarSeverity}
        onClose={handleSnackbarClose}
      />
    </div>
  );
};

export default Profile;
