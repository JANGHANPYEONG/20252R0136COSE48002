/* 웹 화면 상단의 툴바 컴포넌트 */
/* 기업 로고, 유저 정보 및 로그아웃 정보 표시, 유저 아이콘 클릭 시 프로필 페이지로 이동 */
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { styled } from '@mui/material/styles';
// import mui component
import { Typography, IconButton, Toolbar } from '@mui/material';
import MuiAppBar from '@mui/material/AppBar';
// import icons
import PersonOutlineOutlinedIcon from '@mui/icons-material/PersonOutlineOutlined';
import LogoutIcon from '@mui/icons-material/Logout';
// import images
import deeplant_long from '../../../src_assets/deeplant_long.webp';
import logo from '../../../src_assets/logo.png';

// Appbar 스타일 설정
const StyledAppBar = styled(MuiAppBar, {
  shouldForwardProp: (prop) => prop !== 'open' && prop !== 'drawerWidth',
})(({ theme, open, drawerWidth }) => ({
  zIndex: theme.zIndex.drawer + 1,
  transition: theme.transitions.create(['width', 'margin'], {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  backgroundColor: '#FFFFFF',
  boxShadow: 'none',
  minHeight: `${(90 / 1080) * 100}vh`,
  ...(open && {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  }),
}));

const AppBar = ({ open, toggleDrawer, userInfo, logout, drawerWidth }) => {
  const navigate = useNavigate();

  const getTypeColor = (type) => {
    switch (type) {
      case 'Manager':
        return '#70E391';
      case 'Researcher':
        return '#D9C2FF';
      default:
        return '#FFF856';
    }
  };

  return (
    <StyledAppBar position="absolute" open={open} drawerWidth={drawerWidth}>
      <Toolbar
        sx={{
          pr: '24px', // 닫혔을 때 오른쪽 패딩 유지
          ...(open && { minHeight: '120px' }), // 열렸을 때 Toolbar 높이 증가
        }}
      >
        <IconButton
          edge="start"
          aria-label="open drawer"
          onClick={toggleDrawer}
          sx={{
            marginRight: '36px',
            ...(open && { display: 'none' }),
          }}
        >
          <img src={logo} alt="LOGO" />
        </IconButton>
        <Typography sx={{ flexGrow: 1 }}>
          {open && (
            <Link to="/Home">
              <img src={deeplant_long} alt="Deeplant Logo" />
            </Link>
          )}
        </Typography>
        <IconButton onClick={() => navigate('/profile')}>
          <div
            style={{
              backgroundColor: getTypeColor(userInfo.type),
              width: '40px',
              height: '40px',
              borderRadius: '12px',
              marginRight: '10px',
            }}
          >
            <PersonOutlineOutlinedIcon
              style={{ width: '100%', height: '100%' }}
            />
          </div>
          {userInfo && userInfo.name ? (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
              }}
            >
              <Typography
                component="h1"
                variant="h3"
                noWrap
                sx={{ flexGrow: 1, color: 'black', fontSize: '21px' }}
              >
                {userInfo.name}
              </Typography>
              <Typography
                component="h2"
                variant="h3"
                noWrap
                sx={{ flexGrow: 1, fontSize: '12px' }}
              >
                {userInfo.type}
              </Typography>
            </div>
          ) : (
            <Typography component="span" variant="body1" sx={{ flexGrow: 1 }}>
              로그인 필요
            </Typography>
          )}
        </IconButton>
        <IconButton onClick={logout}>
          <div
            style={{
              backgroundColor: '#E8E8E8',
              width: '40px',
              height: '40px',
              borderRadius: '12px',
              marginRight: '10px',
            }}
          >
            <LogoutIcon style={{ width: '100%', height: '100%' }} />
          </div>
        </IconButton>
      </Toolbar>
    </StyledAppBar>
  );
};

export default AppBar;
