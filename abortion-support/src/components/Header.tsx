import React, { useState } from 'react';
import { AppBar, Toolbar, Typography, Button, Box, Container, useTheme, useMediaQuery, IconButton, Drawer, List, ListItem, ListItemText } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import FavoriteIcon from '@mui/icons-material/Favorite';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
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

const MobileNavButton = styled(Button)(({ theme }) => ({
  color: theme.palette.primary.main,
  fontWeight: 600,
  fontSize: '1.1rem',
  padding: '12px 24px',
  width: '100%',
  justifyContent: 'flex-start',
  '&:hover': {
    background: 'rgba(255, 107, 107, 0.1)',
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

  const drawer = (
    <Box sx={{ width: '100%', p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <IconButton onClick={handleDrawerToggle}>
          <CloseIcon />
        </IconButton>
      </Box>
      <List>
        <ListItem>
          <MobileNavButton
            LinkComponent={Link}
            href="/"
            onClick={handleDrawerToggle}
          >
            Главная
          </MobileNavButton>
        </ListItem>
        <ListItem>
          <MobileNavButton
            LinkComponent={Link}
            href="/about"
            onClick={handleDrawerToggle}
          >
            О нас
          </MobileNavButton>
        </ListItem>
        <ListItem>
          <MobileNavButton
            LinkComponent={Link}
            href="/resources"
            onClick={handleDrawerToggle}
          >
            Ресурсы
          </MobileNavButton>
        </ListItem>
        <ListItem>
          <MobileNavButton
            LinkComponent={Link}
            href="/contact"
            onClick={handleDrawerToggle}
          >
            Контакты
          </MobileNavButton>
        </ListItem>
      </List>
    </Box>
  );

  return (
    <StyledAppBar position="sticky">
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          <Box component={Link} to="/" sx={{ flexGrow: 1, textDecoration: 'none' }}>
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
            <Box sx={{ display: 'flex', gap: 2 }}>
              <NavButton
                LinkComponent={Link}
                href="/"
                sx={{
                  background: location.pathname === '/' ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
                }}
              >
                Главная
              </NavButton>
              <NavButton
                LinkComponent={Link}
                href="/about"
                sx={{
                  background: location.pathname === '/about' ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
                }}
              >
                О нас
              </NavButton>
              <NavButton
                LinkComponent={Link}
                href="/resources"
                sx={{
                  background: location.pathname === '/resources' ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
                }}
              >
                Ресурсы
              </NavButton>
              <NavButton
                LinkComponent={Link}
                href="/contact"
                sx={{
                  background: location.pathname === '/contact' ? 'rgba(255, 255, 255, 0.2)' : 'transparent',
                }}
              >
                Контакты
              </NavButton>
            </Box>
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