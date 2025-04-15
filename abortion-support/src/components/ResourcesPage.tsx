import React from 'react';
import { Container, Typography, Box, List, ListItem, ListItemText, Paper } from '@mui/material';

const ResourcesPage: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Полезные ресурсы
        </Typography>
        
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            Медицинские учреждения
          </Typography>
          <List>
            <ListItem>
              <ListItemText
                primary="Клиника репродуктивного здоровья"
                secondary="Адрес: г. Москва, ул. Примерная, 123"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Центр женского здоровья"
                secondary="Адрес: г. Санкт-Петербург, пр. Примерный, 456"
              />
            </ListItem>
          </List>
        </Paper>

        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            Психологическая поддержка
          </Typography>
          <List>
            <ListItem>
              <ListItemText
                primary="Горячая линия психологической помощи"
                secondary="Телефон: 8-800-XXX-XX-XX"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Онлайн-консультации"
                secondary="Доступны через наш сайт ежедневно с 9:00 до 21:00"
              />
            </ListItem>
          </List>
        </Paper>

        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Правовая информация
          </Typography>
          <List>
            <ListItem>
              <ListItemText
                primary="Консультации юриста"
                secondary="Бесплатные консультации по вопросам репродуктивных прав"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Правовые документы"
                secondary="Актуальная информация о законодательстве"
              />
            </ListItem>
          </List>
        </Paper>
      </Box>
    </Container>
  );
};

export default ResourcesPage; 