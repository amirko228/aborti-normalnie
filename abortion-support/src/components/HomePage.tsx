import React from 'react';
import { Container, Typography, Box, Button, Grid, Paper } from '@mui/material';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <>
      <Box id="main" sx={{ my: 4, textAlign: 'center' }}>
        <Container maxWidth="lg">
          <Typography variant="h2" component="h1" gutterBottom>
            Поддержка репродуктивных прав
          </Typography>
          <Typography variant="h5" color="text.secondary" paragraph>
            Мы предоставляем информацию и поддержку для тех, кто нуждается в помощи
          </Typography>
          <Button
            variant="contained"
            color="primary"
            size="large"
            component={Link}
            to="/resources"
            sx={{ mt: 2 }}
          >
            Получить помощь
          </Button>
        </Container>
      </Box>

      <Box id="about" sx={{ py: 8, backgroundColor: 'background.default' }}>
        <Container maxWidth="lg">
          <Typography variant="h3" component="h2" gutterBottom align="center">
            О нас
          </Typography>
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
                <Typography variant="h5" gutterBottom>
                  Наша миссия
                </Typography>
                <Typography>
                  Мы стремимся обеспечить доступ к информации и поддержке для всех, кто в этом нуждается
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
                <Typography variant="h5" gutterBottom>
                  Наши ценности
                </Typography>
                <Typography>
                  Конфиденциальность, профессионализм и поддержка - наши главные приоритеты
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Box id="resources" sx={{ py: 8, backgroundColor: 'background.paper' }}>
        <Container maxWidth="lg">
          <Typography variant="h3" component="h2" gutterBottom align="center">
            Ресурсы
          </Typography>
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
                <Typography variant="h5" gutterBottom>
                  Информация
                </Typography>
                <Typography>
                  Доступ к достоверной информации о репродуктивном здоровье
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
                <Typography variant="h5" gutterBottom>
                  Поддержка
                </Typography>
                <Typography>
                  Профессиональная психологическая и медицинская поддержка
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
                <Typography variant="h5" gutterBottom>
                  Помощь
                </Typography>
                <Typography>
                  Круглосуточная горячая линия: 8 800 555 35 35
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      <Box id="contact" sx={{ py: 8, backgroundColor: 'background.default' }}>
        <Container maxWidth="lg">
          <Typography variant="h3" component="h2" gutterBottom align="center">
            Свяжитесь с нами
          </Typography>
          <Grid container spacing={4} justifyContent="center">
            <Grid item xs={12} md={6}>
              <Paper elevation={3} sx={{ p: 3 }}>
                <Typography variant="h5" gutterBottom>
                  Контактная информация
                </Typography>
                <Typography paragraph>
                  Телефон: 8 800 555 35 35
                </Typography>
                <Typography paragraph>
                  Лучше позвонить чем у кого-то занимать
                </Typography>
                <Typography>
                  Мы работаем круглосуточно, без выходных
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </>
  );
};

export default HomePage; 