/* 웹페이지 위젯바 표시 및 조작 컴포넌트 */

/* 좌측 사이드바 위젯인 Drawer를 불러와 표시 */
import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
// import mui component
import { createTheme, ThemeProvider } from '@mui/material/styles';
// import widget components
import Drawer from './Children/Drawer';

import CustomSnackbar from '../../Base/CustomSnackbar';
import useLogout from '../../../Utils/useLogout';
import { useUser } from '../../../Utils/UserContext';

const MainWidgetBars = () => {
  const [widgetOpen, setWidgetOpen] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const user = useUser();
  const defaultTheme = createTheme();

  const drawerWidth = '260px'; // Width when drawer is open

  const logout = useLogout();

  const handleWidgetToggle = () => {
    setWidgetOpen(!widgetOpen);
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleListItemClick = (item) => {
    // 사용자관리 관련 권한 체크
    if ((item.label === '사용자관리' || item.path === '/UserManagement') && user.type !== 'Manager') {
      setSnackbarMessage('권한이 없습니다');
      setSnackbarOpen(true);
      return;
    }
    
    const queryParams = new URLSearchParams(location.search).toString();
    if (item.label !== '홈' && item.label !== '사용자관리') {
      navigate(`${item.path}?${queryParams}`);
    } else {
      navigate(item.path);
    }
  };

  return (
    <ThemeProvider theme={defaultTheme}>
      <Drawer
        open={widgetOpen}
        toggleDrawer={handleWidgetToggle}
        location={location}
        handleListItemClick={handleListItemClick}
        drawerWidth={drawerWidth}
        userInfo={user}
        logout={logout}
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
