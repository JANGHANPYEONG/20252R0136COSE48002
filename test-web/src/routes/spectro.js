import React from 'react';
import Box from '@mui/material/Box';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import CardActionArea from '@mui/material/CardActionArea';
import Container from '@mui/material/Container';
import { useNavigate } from 'react-router-dom';

import patternImg from '../src_assets/home3.png';
import trainImg from '../src_assets/home1.png';
import predictImg from '../src_assets/home4.png';

const cards = [
  {
    title: '데이터 패턴 분석',
    image: patternImg,
    link: '/spectro/pattern',
  },
  {
    title: '분광 데이터 학습',
    image: trainImg,
    link: '/spectro/train',
  },
  {
    title: '예측하기',
    image: predictImg,
    link: '/spectro/predict',
  },
];

const Spectro = () => {
  const navigate = useNavigate();
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', background: '#FAFBFC' }}>
      <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
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
            분광데이터 관리
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
            MENU
          </Typography>
          <Grid container spacing={8} justifyContent="center">
            {cards.map((card) => (
              <Grid item xs={12} sm={6} md={4} key={card.title}>
                <Box
                  sx={{
                    width: '220px',
                    height: '300px',
                    border: '2px solid rgba(238, 238, 238, 0.50)',
                    borderRadius: '48px',
                    overflow: 'hidden',
                    backgroundColor: 'white',
                    boxShadow: '0 8px 32px 0px rgba(238, 238, 238, 0.50)',
                    padding: '32px 24px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <CardActionArea onClick={() => navigate(card.link)}>
                    <CardMedia
                      sx={{ height: '120px', width: '120px', margin: '0 auto 16px auto' }}
                      image={card.image}
                    />
                    <CardContent>
                      <Typography
                        sx={{ textAlign: 'center', fontSize: '1.2rem', fontWeight: 600 }}
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
      </Box>
    </Box>
  );
};

export default Spectro;
