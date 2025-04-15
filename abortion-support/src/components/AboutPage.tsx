import React from 'react';
import { Container, Typography, Box, Paper, Grid } from '@mui/material';

const AboutPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          О нашей организации
        </Typography>

        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            Наша миссия
          </Typography>
          <Typography paragraph>
            Мы стремимся обеспечить доступ к достоверной информации и поддержке для всех,
            кто нуждается в помощи в вопросах репродуктивного здоровья и прав.
          </Typography>
        </Paper>

        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h5" gutterBottom>
                Наши ценности
              </Typography>
              <Typography>
                • Право на выбор
                • Конфиденциальность
                • Профессионализм
                • Поддержка
                • Доступность информации
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, height: '100%' }}>
              <Typography variant="h5" gutterBottom>
                Наша команда
              </Typography>
              <Typography>
                В нашей команде работают опытные специалисты:
                • Врачи-гинекологи
                • Психологи
                • Юристы
                • Социальные работники
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default AboutPage; 