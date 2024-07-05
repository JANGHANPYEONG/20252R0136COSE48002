import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import UserList from '../components/User/UserList';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';

const Alert = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

function UserManagement() {
  const navigate = useNavigate();
  const [hasPermission, setHasPermission] = useState(true);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const UserInfo = JSON.parse(localStorage.getItem('UserInfo'));

  useEffect(() => {
    if (UserInfo.type !== 'Manager') {
      setHasPermission(false);
      setOpenSnackbar(true);
      setTimeout(() => {
        navigate('/');
      }, 5000); 
    }
  }, [UserInfo, navigate]);

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpenSnackbar(false);
  };

  if (!hasPermission) {
    return (
      <div>
        <Snackbar open={openSnackbar} autoHideDuration={3000} onClose={handleCloseSnackbar}>
          <Alert onClose={handleCloseSnackbar} severity="error">
            권한이 없습니다.
          </Alert>
        </Snackbar>
      </div>
    );
  }

  return <UserList />;
}

export default UserManagement;
