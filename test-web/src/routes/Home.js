import React, { useState } from 'react';
import Box from '@mui/material/Box';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import CardActionArea from '@mui/material/CardActionArea';
import Container from '@mui/material/Container';
import CustomSnackbar from '../components/Base/CustomSnackbar';
import MuiAlert from '@mui/material/Alert';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../Utils/UserContext';
import home_DATA from '../src_assets/home_DATA.png';
import home_ML from '../src_assets/home_ML.png';
import home_PREDICT from '../src_assets/home_PREDICT.png';
import home_USER from '../src_assets/home_USER.png';

const cards = [
  {
    title: '데이터관리',
    subtitle: 'Data',
    image: home_DATA,
    imageSize: { height: '160px', width: '160px' },
    link: '/Data',
  },
  {
    title: 'AI 학습',
    subtitle: 'Learning',
    image: home_ML,
    imageSize: { height: '160px', width: '160px' },
    link: '/AI',
  },
  {
    title: '예측하기',
    subtitle: 'Predict',
    image: home_PREDICT,
    imageSize: { height: '160px', width: '160px' },
    link: '/Predict',
  },
  {
    title: '사용자관리',
    subtitle: 'UserManagement',
    image: home_USER,
    imageSize: { height: '160px', width: '160px' },
    link: '/UserManagement',
  },
];

const Home = () => {
  const navigate = useNavigate();
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const user = useUser();
  const handleCardClick = (link) => {
    if (link === '/UserManagement' && user.type !== 'Manager') {
      setSnackbarOpen(true);
    } else {
      navigate(link);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
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
        <Grid container spacing={4} justifyContent="center" alignItems="center">
          {cards.map((card) => (
            <Grid item xs={12} sm={6} md={3} lg={3} key={card.title} style={{ display: 'flex', justifyContent: 'center' }}>
              <Box
                sx={{
                  width: '240px', // 고정 크기
                  height: '280px', // 고정 크기
                  border: `${(1 / 1920) * 100}vw solid rgba(238, 238, 238, 0.50)`,
                  borderRadius: `${(40 / 1920) * 100}vw`,
                  overflow: 'hidden',
                  backgroundColor: 'white',
                  boxShadow: `${(0 / 1920) * 100}vw ${(4 / 1080) * 100}vh ${(20 / 1920) * 100}vw 0px rgba(238, 238, 238, 0.50)`,
                  padding: `${(20 / 1920) * 100}vw ${(20 / 1080) * 100}vh`,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: `${(0 / 1920) * 100}vw ${(8 / 1080) * 100}vh ${(30 / 1920) * 100}vw 0px rgba(238, 238, 238, 0.70)`,
                  },
                }}
              >
                <CardActionArea onClick={() => handleCardClick(card.link)}>
                  <CardMedia
                    sx={{
                      ...card.imageSize,
                      display: 'block',
                      margin: '0 auto',
                    }}
                    image={card.image}
                  />
                  <CardContent>
                    <Typography
                      sx={{ textAlign: 'center', fontWeight: 600, fontSize: '18px', color: '#151D48' }}
                      gutterBottom
                      variant="h6"
                      component="div"
                    >
                      {card.title}
                    </Typography>
                    <Typography
                      sx={{ textAlign: 'center', fontSize: '14px', color: '#666', fontWeight: 400 }}
                      variant="body2"
                      component="div"
                    >
                      {card.subtitle}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Box>
            </Grid>
          ))}
        </Grid>
        <CustomSnackbar
          open={snackbarOpen}
          message={'권한이 없습니다'}
          severity={'error'}
          onClose={handleSnackbarClose}
        />
      </Container>
    </div>
  );
};

export default Home;
