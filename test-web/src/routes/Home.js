import React, { useState } from 'react';
import Box from '@mui/material/Box';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import CardActionArea from '@mui/material/CardActionArea';
import Container from '@mui/material/Container';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';
import { useNavigate } from 'react-router-dom';

import home1 from '../src_assets/home1.png';
import home2 from '../src_assets/home2.png';
import home3 from '../src_assets/home3.png';
import home4 from '../src_assets/home4.png';
import home5 from '../src_assets/home5.png';
import home6 from '../src_assets/home6.png';

const Alert = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

const cards = [
  {
    title: '홈',
    image: home1,
    imageSize: { height: '106px', width: '104px' },
    link: '/Home',
  },
  {
    title: '대시보드',
    image: home2,
    imageSize: { height: '107px', width: '177px' },
    link: '/DataManage',
  },
  {
    title: '통계 분석',
    image: home3,
    imageSize: { height: `104px`, width: `158px` },
    link: '/stats',
  },
  {
    title: '데이터 예측',
    image: home4,
    imageSize: { height: '100px', width: '100px' },
    link: '/PA',
  },
  {
    title: '사용자 관리',
    image: home5,
    imageSize: { height: '108px', width: '132px' },
    link: '/UserManagement',
  },
  {
    title: '프로필',
    image: home6,
    imageSize: { height: '112px', width: '152px' },
    link: '/Profile',
  },
];

function Home() {
  const navigate = useNavigate();
  const [openSnackbar, setOpenSnackbar] = useState(false);

  const handleCardClick = (link) => {
    const UserInfo = JSON.parse(localStorage.getItem('UserInfo'));
    if (link === '/UserManagement' && UserInfo.type !== 'Manager') {
      setOpenSnackbar(true);
    } else {
      navigate(link);
    }
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpenSnackbar(false);
  };

  return (
    <div
      style={{
        // alignContent: 'center',
        overflow: 'auto',
        // width: '100%',
        marginTop: '100px',
        paddingBottom: '100px',
        // height: '100%',
        // paddingLeft: '30px',
        // paddingRight: '20px',
      }}
    >
      <Container maxWidth="md">
      <Typography
          variant="h4" // Typography의 variant를 조정하여 원하는 스타일과 크기를 선택할 수 있습니다.
          sx={{
            color: '#151D48',
            fontFamily: 'Poppins',
            fontSize: `30px`, // 상대적인 크기
            fontStyle: 'normal',
            fontWeight: 600,
            lineHeight: `${(50.4 / 1080) * 100}vh`, // 상대적인 크기
            marginBottom: `${(20 / 1080) * 100}vh`,
          }}
        >
          Home
        </Typography>
        <Typography
          variant="h4" // Typography의 variant를 조정하여 원하는 스타일과 크기를 선택할 수 있습니다.
          sx={{
            color: '#151D48',
            fontFamily: 'Poppins',
            fontSize: `36px`, // 상대적인 크기
            fontStyle: 'normal',
            fontWeight: 600,
            lineHeight: `${(50.4 / 1080) * 100}vh`, // 상대적인 크기
            marginBottom: `${(58 / 1080) * 100}vh`,
          }}
        >
          원하시는 작업을 선택해주세요.
        </Typography>
        <Grid container spacing={5}>
          {cards.map((card) => (
            <Grid item xs={12} sm={4} md={4} lg={4} key={card.title}>
              <Box
                sx={{
                  // width: `${(260 / 1920) * 100}vw`, // Relative width
                  // height: `${(260 / 1080) * 100}vh`, // Relative height
                  border: `${(1 / 1920) * 100}vw solid rgba(238, 238, 238, 0.50)`, // Relative border
                  borderRadius: `${(40 / 1920) * 100}vw`, // Relative border radius
                  overflow: 'hidden',
                  backgroundColor: 'white',
                  boxShadow: `${(0 / 1920) * 100}vw ${(4 / 1080) * 100}vh ${(20 / 1920) * 100}vw 0px rgba(238, 238, 238, 0.50)`, // Relative boxShadow
                  padding: `${(20 / 1920) * 100}vw ${(20 / 1080) * 100}vh`, // Relative padding
                }}
              >
                <CardActionArea onClick={() => handleCardClick(card.link)}>
                  <CardMedia
                    sx={{
                      ...card.imageSize,
                      margin: ' auto',
                    }}
                    image={card.image}
                  />
                  <CardContent>
                    <Typography
                      sx={{ textAlign: 'center' }}
                      gutterBottom
                      variant="h6"
                      component="div"
                    >
                      {card.title}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Box>
            </Grid>
          ))}
        </Grid>
        <Snackbar
          open={openSnackbar}
          autoHideDuration={3000}
          onClose={handleCloseSnackbar}
        >
          <Alert onClose={handleCloseSnackbar} severity="error">
            권한이 없습니다
          </Alert>
        </Snackbar>
      </Container>
    </div>
  );
}

export default Home;
