import React from 'react';
import { Box, Container, Typography, Link as MuiLink } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 3,
        px: 2,
        mt: 'auto',
        backgroundColor: '#f8bbd0',
      }}
    >
      <Container maxWidth="lg">
        <Typography variant="body2" color="text.secondary" align="center">
          {'© '}
          {new Date().getFullYear()}
          {' '}
          <MuiLink color="inherit" href="#">
            Поддержка репродуктивных прав
          </MuiLink>
          {'. Все права защищены.'}
        </Typography>
        <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
          Контактная информация: support@example.com
        </Typography>
      </Container>
    </Box>
  );
};

export default Footer; 