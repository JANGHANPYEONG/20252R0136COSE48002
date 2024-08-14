import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../Utils/UserContext';

import UserList from '../components/UserManagement/UserMangementField';
import CustomSnackbar from '../components/Base/CustomSnackbar';
// import MuiAlert from '@mui/material/Alert';

// const Alert = React.forwardRef((props, ref) => {
//   return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
// });

const UserManagement = () => {
  const navigate = useNavigate();
  const [hasPermission, setHasPermission] = useState(true);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  // const UserInfo = JSON.parse(localStorage.getItem('UserInfo'));
  const user = useUser();
  useEffect(() => {
    if (user.type !== 'Manager') {
      setHasPermission(false);
      setSnackbarOpen(true);
      setTimeout(() => {
        navigate('/');
      }, 2500);
    }
  }, [user, navigate]);

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  if (!hasPermission) {
    return (
      <div>
        <CustomSnackbar
          open={snackbarOpen}
          message={'권한이 없습니다.'}
          severity={'error'}
          onClose={handleSnackbarClose}
        />
      </div>
    );
  }

  return <UserList />;
};

export default UserManagement;
