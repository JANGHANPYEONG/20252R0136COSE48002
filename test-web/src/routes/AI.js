import React from 'react';
import { useNavigate } from 'react-router-dom';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Typography from '@mui/material/Typography';
import CardActionArea from '@mui/material/CardActionArea';
import Container from '@mui/material/Container';
import data_ANA from '../src_assets/data_ANA.png';
import home_ML from '../src_assets/home_ML.png';

const cards = [
    {
        title: '패턴분석',
        image: data_ANA,
        link: '/Pattern',
    },
    {
        title: '학습하기',
        image: home_ML,
        link: '/Learning',
    },
];

const AI = () => {
    const navigate = useNavigate();
    return (
        <div style={{ marginTop: '100px', paddingBottom: '100px' }}>
            <Container maxWidth="sm">
                <Typography
                    variant="h4"
                    sx={{
                        color: '#151D48',
                        fontFamily: 'Poppins',
                        fontSize: `30px`,
                        fontWeight: 600,
                        marginBottom: '20px',
                    }}
                >
                    AI 학습
                </Typography>
                <Grid container spacing={5} justifyContent="center" alignItems="center">
                    {cards.map((card) => (
                        <Grid item xs={12} sm={6} md={6} lg={6} key={card.title} style={{ display: 'flex', justifyContent: 'center' }}>
                            <Box
                                sx={{
                                    width: '240px',
                                    height: '260px',
                                    border: '1px solid rgba(238, 238, 238, 0.50)',
                                    borderRadius: '40px',
                                    overflow: 'hidden',
                                    backgroundColor: 'white',
                                    boxShadow: '0 4px 20px 0px rgba(238, 238, 238, 0.50)',
                                    padding: '20px',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    transition: 'transform 0.2s, box-shadow 0.2s',
                                    '&:hover': {
                                        transform: 'translateY(-5px)',
                                        boxShadow: '0 8px 30px 0px rgba(238, 238, 238, 0.70)',
                                    },
                                }}
                            >
                                <CardActionArea onClick={() => navigate(card.link)}>
                                    <CardMedia
                                        sx={{ height: '120px', width: '120px', display: 'block', margin: '0 auto' }}
                                        image={card.image}
                                    />
                                    <CardContent>
                                        <Typography sx={{ textAlign: 'center', fontWeight: 600, fontSize: '18px', color: '#151D48' }} gutterBottom variant="h6" component="div">
                                            {card.title}
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
};

export default AI; 