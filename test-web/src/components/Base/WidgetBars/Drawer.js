/* 웹 화면 좌측의 사이드바 컴포넌트 */

/* 토글 버튼으로 사이드 바가 열리고, 아이콘 클릭 시 해당 페이지로 이동 */
import React from 'react';
import { styled } from '@mui/material/styles';
// import mui component
import {
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Toolbar,
  Tooltip,
} from '@mui/material';
import MuiDrawer from '@mui/material/Drawer';
// import icons
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
// import page lists
import pageListItems from './pageListItems';

// Drawer 스타일 설정
const StyledDrawer = styled(MuiDrawer, {
  shouldForwardProp: (prop) => prop !== 'open' && prop !== 'drawerWidth',
})(({ theme, open, drawerWidth }) => ({
  '& .MuiDrawer-paper': {
    position: 'relative',
    whiteSpace: 'nowrap',
    width: open ? drawerWidth : '64px',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
    boxSizing: 'border-box',
    backgroundColor: '#FFFFFF', //사이드바 배경
    boxShadow: `${(5 / 1920) * 100}vw 0px ${(30 / 1080) * 100}vh 0px rgba(238, 238, 238, 0.50)`, // 사이드바 그림자
    overflowX: 'hidden',
    ...(!open && {
      transition: theme.transitions.create('width', {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
      width: '64px', // 고정된 너비 설정
      [theme.breakpoints.up('sm')]: {
        width: '64px', // sm 브레이크포인트 이상에서도 동일한 너비 유지
      },
    }),
  },
}));

const Drawer = ({
  open,
  toggleDrawer,
  location,
  handleListItemClick,
  drawerWidth,
}) => {
  const mainListItems = pageListItems;

  return (
    <StyledDrawer variant="permanent" open={open} drawerWidth={drawerWidth}>
      <Toolbar />
      <List
        component="nav"
        sx={{
          pt: '14px', // 홈 버튼에만 추가 상단 패딩
          pb: '12px', // 홈 버튼에만 추가 하단 패딩
          ...(open && { mt: '8px' }), // 열렸을 때 추가 상단 여백
        }}
      >
        {mainListItems.map((item) => (
          <Tooltip title={item.label} placement="right" arrow key={item.label}>
            <ListItemButton
              component="div"
              onClick={() => handleListItemClick(item)}
              selected={location.pathname === item.path}
              sx={{
                margin: '0 auto 16px auto',
                width: open ? 245 : 64,
                height: 64,
                display: 'flex',
                justifyContent: 'flex-start',
                alignItems: 'center',
                ...(location.pathname === item.path && {
                  '& .MuiSvgIcon-root, .MuiTypography-root': {
                    color: '#FFFFFF',
                  },
                  '&.Mui-selected': {
                    backgroundColor: '#7BD758',
                    borderRadius: '16px',
                    boxShadow: 3,
                  },
                }),
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{ color: 'textPrimary' }}
              />
            </ListItemButton>
          </Tooltip>
        ))}
      </List>
      <Toolbar
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          px: [1.2],
        }}
      >
        <IconButton onClick={toggleDrawer}>
          {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </Toolbar>
    </StyledDrawer>
  );
};

export default Drawer;
