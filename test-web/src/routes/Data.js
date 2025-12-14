import React from 'react';
import { useNavigate } from 'react-router-dom';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import CardActionArea from '@mui/material/CardActionArea';
import Container from '@mui/material/Container';
import home_DATA from '../src_assets/home_DATA.png';
import data_BOARD from '../src_assets/data_BOARD.png';
import data_ANA from '../src_assets/data_ANA.png';
import home_ML from '../src_assets/home_ML.png';
import data from '../src_assets/data.png';
const cards = [
    {
        title: '데이터등록',
        subtitle: 'Data Registration',
        image: home_DATA,
        link: '/DataRegister',
    },
    {
        title: '파장등록',
        subtitle: 'Spectral Registration',
        image: data,
        link: '/spectrals',
    },
    {
        title: '대시보드',
        subtitle: 'Dashboard',
        image: data_BOARD,
        link: '/DashBoard',
    },
    {
        title: '통계분석',
        subtitle: 'Statistics',
        image: data_ANA,
        link: '/Stats',
    },
];

const Data = () => {
    const navigate = useNavigate();
    return (
        <div
          style={{
            overflow: 'auto',
            marginTop: '30px',
            paddingBottom: '50px',
            width: '100%',
          }}
        >
            <Container maxWidth="lg">
                <Box 
                  sx={{
                    textAlign: 'center',
                    mb: 4,
                    pb: 2,
                    borderBottom: '1px solid rgba(0,0,0,0.08)'
                  }}
                >
                  <Typography
                    variant="h3"
                    sx={{
                      color: '#151D48',
                      fontFamily: 'Poppins, sans-serif',
                      fontSize: { xs: '26px', sm: '30px', md: '34px' },
                      fontWeight: 700,
                      mb: 1,
                    }}
                  >
                    데이터관리
                  </Typography>
                  <Typography
                    variant="h4"
                    sx={{
                      color: '#151D48',
                      fontFamily: 'Poppins, sans-serif',
                      fontSize: { xs: '20px', sm: '24px', md: '28px' },
                      fontWeight: 600,
                      mb: 2,
                    }}
                  >
                    원하시는 작업을 선택해주세요
                  </Typography>
                </Box>
                <Grid 
                  container 
                  spacing={{ xs: 2, sm: 3, md: 4 }} 
                  justifyContent="center" 
                  alignItems="stretch" 
                  sx={{ 
                    mt: { xs: 2, sm: 3, md: 4 },
                    px: { xs: 1, sm: 2, md: 3 }
                  }}
                >
                    {cards.map((card) => (
                        <Grid 
                          item 
                          xs={12} 
                          sm={6} 
                          md={3} 
                          lg={3} 
                          key={card.title} 
                          sx={{ 
                            display: 'flex',
                            mb: { xs: 2, sm: 0 }
                          }}>
                            <Box
                                sx={{
                                  width: '100%', // 전체 너비 사용
                                  minHeight: '240px', // 최소 높이 설정
                                  border: `1px solid rgba(238, 238, 238, 0.70)`,
                                  borderRadius: '16px',
                                  overflow: 'hidden',
                                  backgroundColor: 'white',
                                  boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.05)',
                                  display: 'flex',
                                  flexDirection: 'column',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                                  '&:hover': {
                                    transform: 'translateY(-5px)',
                                    boxShadow: '0px 8px 20px rgba(0, 0, 0, 0.12)',
                                  },
                                }}
                            >
                            <CardActionArea 
                              onClick={() => navigate(card.link)}
                              sx={{
                                height: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                                justifyContent: 'center',
                                padding: '16px',
                              }}
                            >
                                <CardMedia
                                    component="img"
                                    sx={{
                                      width: '100px', // 이미지 크기 조정
                                      height: '100px',
                                      objectFit: 'contain',
                                      margin: '0 auto 16px',
                                    }}
                                    image={card.image}
                                    alt={card.title}
                                />
                                <CardContent sx={{ padding: '8px 16px', textAlign: 'center' }}>
                                    <Typography
                                      sx={{ 
                                        fontWeight: 600, 
                                        fontSize: '20px', 
                                        color: '#151D48',
                                        lineHeight: 1.3,
                                        marginBottom: '8px'
                                      }}
                                      variant="h6"
                                      component="div"
                                    >
                                        {card.title}
                                    </Typography>
                                    <Typography
                                      sx={{ 
                                        fontSize: '14px', 
                                        color: '#666', 
                                        fontWeight: 500,
                                        letterSpacing: '0.5px' 
                                      }}
                                      variant="body2"
                                    >
                                        {card.subtitle}
                                    </Typography>
                                </CardContent>
                            </CardActionArea>
                            </Box>
                        </Grid>
                    ))}
                </Grid>
            </Container>
        </div>
    );
};export default Data; 