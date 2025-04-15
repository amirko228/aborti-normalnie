import React, { useState } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Container, useTheme, useMediaQuery, IconButton, Drawer, List, ListItem, Stack } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import FavoriteIcon from '@mui/icons-material/Favorite';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import PhoneIcon from '@mui/icons-material/Phone';
import { styled } from '@mui/material/styles';

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  background: 'linear-gradient(45deg, #ff6b6b 30%, #ff8e8e 90%)',
  boxShadow: '0 3px 20px rgba(255, 107, 107, 0.3)',
  transition: 'all 0.3s ease',
  '&:hover': {
    boxShadow: '0 5px 25px rgba(255, 107, 107, 0.4)',
  },
}));

const Logo = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'scale(1.05) rotate(-2deg)',
  },
}));

const NavButton = styled(Button)(({ theme }) => ({
  color: 'white',
  fontWeight: 600,
  fontSize: '1rem',
  padding: '8px 16px',
  borderRadius: '25px',
  transition: 'all 0.3s ease',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    background: 'rgba(255, 255, 255, 0.1)',
    transform: 'translateX(-100%)',
    transition: 'transform 0.3s ease',
  },
  '&:hover': {
    background: 'rgba(255, 255, 255, 0.1)',
    transform: 'translateY(-2px)',
    '&::before': {
      transform: 'translateX(0)',
    },
  },
}));

const PhoneNumber = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'flex-end',
  color: 'white',
  marginRight: theme.spacing(4),
  '& .phone': {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1),
    fontSize: '1.2rem',
    fontWeight: 700,
    textDecoration: 'none',
    color: 'white',
    transition: 'all 0.3s ease',
    '&:hover': {
      transform: 'scale(1.05)',
    },
  },
  '& .slogan': {
    fontSize: '0.8rem',
    opacity: 0.9,
    fontStyle: 'italic',
  },
}));

const Header: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const drawer = (
    <Box sx={{ width: '100%', p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ color: theme.palette.primary.main }}>
          8 800 555 35 35
        </Typography>
        <IconButton onClick={handleDrawerToggle}>
          <CloseIcon />
        </IconButton>
      </Box>
      <List>
        <ListItem>
          <Button
            fullWidth
            onClick={() => {
              scrollToSection('main');
              handleDrawerToggle();
            }}
          >
            Главная
          </Button>
        </ListItem>
        <ListItem>
          <Button
            fullWidth
            onClick={() => {
              scrollToSection('about');
              handleDrawerToggle();
            }}
          >
            О нас
          </Button>
        </ListItem>
        <ListItem>
          <Button
            fullWidth
            onClick={() => {
              scrollToSection('resources');
              handleDrawerToggle();
            }}
          >
            Ресурсы
          </Button>
        </ListItem>
        <ListItem>
          <Button
            fullWidth
            onClick={() => {
              scrollToSection('contact');
              handleDrawerToggle();
            }}
          >
            Контакты
          </Button>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <StyledAppBar position="sticky">
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ justifyContent: 'space-between' }}>
          <Box component={Link} to="/" sx={{ textDecoration: 'none', display: 'flex', alignItems: 'center' }}>
            <Logo>
              <FavoriteIcon sx={{ color: 'white', fontSize: 36 }} />
              <Typography
                variant="h5"
                component="div"
                sx={{
                  color: 'white',
                  fontWeight: 700,
                  letterSpacing: '1px',
                  textShadow: '0 2px 4px rgba(0,0,0,0.1)',
                }}
              >
                Поддержка репродуктивных прав
              </Typography>
            </Logo>
          </Box>

          {!isMobile && (
            <Stack direction="row" spacing={4} alignItems="center">
              <PhoneNumber>
                <a href="tel:88005553535" className="phone">
                  <PhoneIcon />
                  8 800 555 35 35
                </a>
                <span className="slogan">Лучше позвонить чем у кого-то занимать</span>
              </PhoneNumber>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <NavButton onClick={() => scrollToSection('main')}>
                  Главная
                </NavButton>
                <NavButton onClick={() => scrollToSection('about')}>
                  О нас
                </NavButton>
                <NavButton onClick={() => scrollToSection('resources')}>
                  Ресурсы
                </NavButton>
                <NavButton onClick={() => scrollToSection('contact')}>
                  Контакты
                </NavButton>
              </Box>
            </Stack>
          )}

          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="end"
              onClick={handleDrawerToggle}
              sx={{ ml: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
        </Toolbar>
      </Container>

      <Drawer
        variant="temporary"
        anchor="right"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          '& .MuiDrawer-paper': {
            width: '100%',
            maxWidth: '400px',
          },
        }}
      >
        {drawer}
      </Drawer>
    </StyledAppBar>
  );
};

export default Header; 