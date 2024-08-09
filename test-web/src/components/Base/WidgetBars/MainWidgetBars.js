/* 웹페이지 위젯바 표시 및 조작 컴포넌트 */

/* 화면 상단 및 좌측 위젯인 AppBar와 Drawer를 불러와 표시 */
import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

// import mui component
import { createTheme, ThemeProvider } from '@mui/material/styles';
// import images
import CustomSnackbar from '../../Base/CustomSnackbar';
import useLogout from '../../../Utils/useLogout';
// import widget components
import AppBar from './AppBar';
import Drawer from './Drawer';

const MainWidgetBars = () => {
  const [widgetOpen, setWidgetOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [userInfo, setUserInfo] = useState(
    JSON.parse(localStorage.getItem('UserInfo'))
  );
  const defaultTheme = createTheme();

  // const drawerWidth = `${(345 / 1920) * 100}vw`;
  const drawerWidth = '345px'; // Width when drawer is open

  // 같은 탭 내에서의 변경(프로필 이름, 권한 등)을 감지하기 위한 useEffect, 커스텀 이벤트 리스너
  useEffect(() => {
    const handleStorageChange = () => {
      const updatedUserInfo = JSON.parse(localStorage.getItem('UserInfo'));
      setUserInfo(updatedUserInfo);
    };
    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('userInfoUpdated', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('userInfoUpdated', handleStorageChange);
    };
  }, []);

  const logout = useLogout();

  const toggleDrawer = () => {
    setWidgetOpen(!widgetOpen);
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleListItemClick = (item) => {
    if (item.label === '사용자 관리' && userInfo.type !== 'Manager') {
      setSnackbarMessage('권한이 없습니다');
      setSnackbarOpen(true);
    } else {
      const queryParams = new URLSearchParams(location.search).toString();
      if (item.label !== '홈' && item.label !== '사용자 관리') {
        navigate(`${item.path}?${queryParams}`);
      } else {
        navigate(item.path);
      }
    }
  };

  return (
    <ThemeProvider theme={defaultTheme}>
      <AppBar
        open={widgetOpen}
        toggleDrawer={toggleDrawer}
        userInfo={userInfo}
        logout={logout}
        drawerWidth={drawerWidth}
      />
      <Drawer
        open={widgetOpen}
        toggleDrawer={toggleDrawer}
        location={location}
        handleListItemClick={handleListItemClick}
        drawerWidth={drawerWidth}
      />
      <CustomSnackbar
        open={snackbarOpen}
        message={snackbarMessage}
        severity={'error'}
        onClose={handleSnackbarClose}
      />
    </ThemeProvider>
  );
};

export default MainWidgetBars;
