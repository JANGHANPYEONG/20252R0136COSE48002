import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import { CircularProgress } from '@mui/material';
import { userUpdate } from '../../API/user/userUpdate';
import { format } from 'date-fns';

const navy = '#0F3659';

const ProfileEditForm = ({
  userInfo,
  onUpdate,
  onDeleteRequest,
  handleShowSnackbar,
}) => {
  const [updatedUserInfo, setUpdatedUserInfo] = useState(userInfo);
  const [isUpdating, setIsUpdating] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setUpdatedUserInfo((prev) => ({ ...prev, [name]: value }));
  };

  const updateUserInfo = async () => {
    setIsUpdating(true);
    try {
      const response = await userUpdate({
        userId: userInfo.userId,
        name: updatedUserInfo.name,
        homeAddr: updatedUserInfo.homeAddr,
        company: updatedUserInfo.company,
        jobTitle: updatedUserInfo.jobTitle,
      });

      const date = await response.json();

      if (response.ok) {
        const formattedCreatedAt = format(
          new Date(date.createdAt),
          'yyyy-MM-dd'
        );
        const formattedUpdatedAt = format(
          new Date(date.updatedAt),
          'yyyy-MM-dd'
        );

        const updatedData = {
          ...updatedUserInfo,
          updatedAt: formattedUpdatedAt,
          createdAt: formattedCreatedAt,
        };

        onUpdate(updatedData);
        handleShowSnackbar('회원정보가 수정되었습니다.', 'success');
      } else {
        handleShowSnackbar('회원정보 수정에 실패했습니다.', 'error');
      }
    } catch (error) {
      console.log('Error updating user information:', error);
      handleShowSnackbar('서버와 통신 중 오류가 발생했습니다.', 'error');
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <div style={{ marginBottom: '1rem' }}>
        <TextField
          label="회원가입일"
          name="createdAt"
          value={updatedUserInfo.createdAt}
          disabled
          fullWidth
        />
      </div>
      <div style={{ marginBottom: '1rem' }}>
        <TextField
          label="업데이트일"
          name="updatedAt"
          value={updatedUserInfo.updatedAt}
          disabled
          fullWidth
        />
      </div>
      <div style={{ marginBottom: '1rem' }}>
        <TextField
          label="권한"
          name="type"
          value={updatedUserInfo.type}
          disabled
          fullWidth
        />
      </div>
      <div style={{ marginBottom: '1rem' }}>
        <TextField
          label="이름"
          name="name"
          value={updatedUserInfo.name}
          onChange={handleInputChange}
          fullWidth
        />
      </div>
      <div style={{ marginBottom: '1rem' }}>
        <TextField
          label="직장"
          name="company"
          value={updatedUserInfo.company}
          onChange={handleInputChange}
          fullWidth
        />
      </div>
      <div style={{ marginBottom: '1rem' }}>
        <TextField
          label="직책"
          name="jobTitle"
          value={updatedUserInfo.jobTitle}
          onChange={handleInputChange}
          fullWidth
        />
      </div>
      <div style={{ marginBottom: '1rem' }}>
        <TextField
          label="주소"
          name="homeAddr"
          value={updatedUserInfo.homeAddr}
          onChange={handleInputChange}
          fullWidth
        />
      </div>
      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <Button
          style={{ backgroundColor: navy, margin: '0.5rem' }}
          variant="contained"
          onClick={updateUserInfo}
          disabled={isUpdating}
        >
          {isUpdating ? <CircularProgress size={24} /> : '정보 수정'}
        </Button>
        <Button
          variant="contained"
          onClick={onDeleteRequest}
          style={{
            backgroundColor: 'grey',
            color: 'white',
            margin: '0.5rem',
          }}
        >
          회원 탈퇴
        </Button>
      </div>
    </Paper>
  );
};

export default ProfileEditForm;
