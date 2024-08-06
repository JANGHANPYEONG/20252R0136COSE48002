import React, { useState } from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import { useNavigate } from 'react-router-dom';
import CustomSnackbar from '../components/Base/CustomSnackbar';
import { userDelete } from '../API/user/userDelete';
import ProfileEditForm from '../components/Profile/ProfileEditForm';
import PasswordCheckModal from '../components/Profile/PasswordCheckModal';
import SelfDeleteConfirmationModal from '../components/Profile/SelfDeleteConfirmationModal';

const Profile = () => {
  const [userInfo, setUserInfo] = useState(
    JSON.parse(localStorage.getItem('UserInfo'))
  );
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  const navigate = useNavigate();

  const handleShowSnackbar = (message, severity) => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleUpdate = (updatedData) => {
    setUserInfo(updatedData);
    localStorage.setItem('UserInfo', JSON.stringify(updatedData));
    window.dispatchEvent(new Event('userInfoUpdated'));
    handleShowSnackbar('회원정보가 수정되었습니다.', 'success');
  };

  const handleDeleteRequest = () => {
    setIsPasswordModalOpen(true);
  };

  const handlePasswordSuccess = () => {
    setIsConfirmModalOpen(true);
  };

  const deleteself = async () => {
    try {
      const response = await userDelete(userInfo.userId);

      if (response.ok) {
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
      <Paper sx={{ p: 2 }}>
        <ProfileEditForm
          userInfo={userInfo}
          onUpdate={handleUpdate}
          onDeleteRequest={handleDeleteRequest}
          handleShowSnackbar={handleShowSnackbar}
        />
      </Paper>

      <PasswordCheckModal
        isOpen={isPasswordModalOpen}
        onClose={() => setIsPasswordModalOpen(false)}
        onSuccess={handlePasswordSuccess}
      />

      <SelfDeleteConfirmationModal
        isOpen={isConfirmModalOpen}
        onClose={() => setIsConfirmModalOpen(false)}
        onConfirm={deleteself}
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
