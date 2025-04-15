import React from 'react';
import { Container, Typography, Box, Paper, TextField, Button, Grid } from '@mui/material';

const ContactPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Свяжитесь с нами
        </Typography>

        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                Контактная информация
              </Typography>
              <Typography paragraph>
                Телефон: 8-800-XXX-XX-XX
              </Typography>
              <Typography paragraph>
                Email: support@example.com
              </Typography>
              <Typography paragraph>
                Адрес: г. Москва, ул. Примерная, 123
              </Typography>
              <Typography paragraph>
                Часы работы: Пн-Пт с 9:00 до 21:00
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3 }}>
              <Typography variant="h5" gutterBottom>
                Форма обратной связи
              </Typography>
              <Box component="form" noValidate sx={{ mt: 1 }}>
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="name"
                  label="Ваше имя"
                  name="name"
                  autoComplete="name"
                  autoFocus
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  id="email"
                  label="Email"
                  name="email"
                  autoComplete="email"
                />
                <TextField
                  margin="normal"
                  required
                  fullWidth
                  name="message"
                  label="Сообщение"
                  type="text"
                  id="message"
                  multiline
                  rows={4}
                />
                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  sx={{ mt: 3, mb: 2 }}
                >
                  Отправить
                </Button>
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default ContactPage; 