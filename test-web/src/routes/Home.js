import Box from '@mui/material/Box';
import React from 'react';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import CardActionArea from '@mui/material/CardActionArea';
import { useNavigate } from 'react-router-dom';
import Container from '@mui/material/Container';

import home1 from '../src_assets/home1.png';
import home2 from '../src_assets/home2.png';
import home3 from '../src_assets/home3.png';
import home4 from '../src_assets/home4.png';
import home5 from '../src_assets/home5.png';
import home6 from '../src_assets/home6.png';

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
  const handleCardClick = (link) => {
    navigate(link);
  };

  return (
    <Container maxWidth="md">
      <Typography
        variant="h4" // Typography의 variant를 조정하여 원하는 스타일과 크기를 선택할 수 있습니다.
        sx={{
          color: '#151D48',
          fontFamily: 'Poppins',
          fontSize: `${(36 / 1920) * 100}vw`, // 상대적인 크기
          fontStyle: 'normal',
          fontWeight: 600,
          lineHeight: `${(50.4 / 1080) * 100}vh`, // 상대적인 크기
          marginBottom: `${(58 / 1080) * 100}vh`,
        }}
      >
        원하시는 작업을 선택해주세요
      </Typography>
      <Grid container spacing={5}>
        {cards.map((card) => (
          <Grid item xs={12} sm={4} md={4} lg={4} key={card}>
            <Box
              sx={{
                width: `${(261 / 1920) * 100}vw`, // Relative width
                height: `${(260 / 1080) * 100}vh`, // Relative height
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
    </Container>
  );
}

export default Home;
