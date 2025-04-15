import React from 'react';
import { Container, Typography, Box, Button, Grid, Paper } from '@mui/material';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4, textAlign: 'center' }}>
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
      </Box>

      <Grid container spacing={4} sx={{ mt: 4 }}>
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
            <Typography variant="h5" gutterBottom>
              Информация
            </Typography>
            <Typography>
              Доступ к достоверной информации о репродуктивном здоровье и правах
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
              Ресурсы
            </Typography>
            <Typography>
              Список проверенных медицинских учреждений и специалистов
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default HomePage; 