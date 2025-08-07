/* 웹 화면 좌측의 사이드바 컴포넌트 */

/* 토글 버튼으로 사이드 바가 열리고, 아이콘 클릭 시 해당 페이지로 이동 */
import React, { useState, useEffect } from 'react';
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
  Collapse,
} from '@mui/material';
import MuiDrawer from '@mui/material/Drawer';
// import icons
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
// import page lists
import pageListItems from '../constants/pageListItems';

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
  drawerWidth
}) => {
  const [expandedMenus, setExpandedMenus] = useState({});

  // 사이드바가 축소될 때 하위 메뉴도 함께 접기
  useEffect(() => {
    if (!open) {
      setExpandedMenus({});
    }
  }, [open]);

  // 경로가 바뀔 때마다, 해당 경로가 속한 상위 메뉴만 펼치고 나머지는 접음
  useEffect(() => {
    let found = false;
    const newExpanded = {};
    for (const item of pageListItems) {
      if (item.hasSubmenu) {
        if (
          location.pathname === item.path ||
          item.submenu.some((sub) => location.pathname === sub.path)
        ) {
          newExpanded[item.label] = true;
          found = true;
        } else {
          newExpanded[item.label] = false;
        }
      }
    }
    setExpandedMenus(newExpanded);
  }, [location.pathname]);

  const handleMenuExpand = (label) => {
    setExpandedMenus(prev => ({
      ...prev,
      [label]: !prev[label]
    }));
  };

  const isPathInSubmenu = (item) => {
    if (!item.hasSubmenu) return false;
    return item.submenu.some(subItem => location.pathname === subItem.path);
  };

  const renderMenuItem = (item) => {
    const isSelected = location.pathname === item.path || isPathInSubmenu(item);
    const isExpanded = expandedMenus[item.label];

    return (
      <React.Fragment key={item.label}>
        <Tooltip title={item.label} placement="right" arrow>
          <ListItemButton
            component="div"
            onClick={() => {
              if (item.hasSubmenu) {
                handleMenuExpand(item.label);
                handleListItemClick(item);
              } else {
                handleListItemClick(item);
              }
            }}
            selected={isSelected}
            sx={{
              margin: '0 auto 8px auto',
              width: open ? 245 : 64,
              height: 64,
              display: 'flex',
              justifyContent: 'flex-start',
              alignItems: 'center',
              ...(isSelected && {
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
            {open && (
              <>
                <ListItemText
                  primary={item.label}
                  primaryTypographyProps={{ color: 'textPrimary' }}
                />
                {item.hasSubmenu && (
                  <IconButton size="small">
                    {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                )}
              </>
            )}
          </ListItemButton>
        </Tooltip>

        {item.hasSubmenu && (
          <Collapse in={isExpanded && open} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.submenu.map((subItem) => {
                const isSubSelected = location.pathname === subItem.path;
                return (
                  <Tooltip title={subItem.label} placement="right" arrow key={subItem.path}>
                    <ListItemButton
                      component="div"
                      onClick={() => handleListItemClick(subItem)}
                      selected={isSubSelected}
                      sx={{
                        margin: '0 auto 4px auto',
                        width: open ? 220 : 64,
                        height: 48,
                        marginLeft: open ? 3 : 0,
                        display: 'flex',
                        justifyContent: 'flex-start',
                        alignItems: 'center',
                        ...(isSubSelected && {
                          '& .MuiTypography-root': {
                            color: '#FFFFFF',
                          },
                          '&.Mui-selected': {
                            backgroundColor: '#7BD758',
                            borderRadius: '12px',
                            boxShadow: 2,
                          },
                        }),
                      }}
                    >
                      {open && (
                        <ListItemText
                          primary={subItem.label}
                          primaryTypographyProps={{
                            color: 'textPrimary',
                            fontSize: '0.9rem'
                          }}
                        />
                      )}
                    </ListItemButton>
                  </Tooltip>
                );
              })}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  return (
    <StyledDrawer variant="permanent" open={open} drawerWidth={drawerWidth}>
      <Toolbar />
      <List
        component="nav"
        sx={{
          pt: '14px',
          pb: '12px',
          ...(open && { mt: '8px' }),
        }}
      >
        {pageListItems.map(renderMenuItem)}
      </List>
      <Toolbar
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          px: [1.2],
        }}
      >
      </Toolbar>
    </StyledDrawer>
  );
};

export default Drawer;
