import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Box,
  ListItemButton,
  Tooltip
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Category,
  Inventory,
  People,
  Person,
  ShoppingCart,
  Logout
} from '@mui/icons-material';
import { useNavigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const drawerWidth = 240;
const miniDrawerWidth = 72;

const Layout: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  const navigate = useNavigate();
  const { logout, user } = useAuth();

  // Detectar si es móvil para comportamiento responsive
  useEffect(() => {
    const checkIsMobile = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      // En móvil, el drawer empieza cerrado
      if (mobile) {
        setDrawerOpen(false);
      }
    };
    
    checkIsMobile();
    window.addEventListener('resize', checkIsMobile);
    
    return () => window.removeEventListener('resize', checkIsMobile);
  }, []);

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
    { text: 'Categorías', icon: <Category />, path: '/categorias' },
    { text: 'Productos', icon: <Inventory />, path: '/productos' },
    { text: 'Clientes', icon: <People />, path: '/clientes' },
    { text: 'Usuarios', icon: <Person />, path: '/usuarios' },
    { text: 'Ventas', icon: <ShoppingCart />, path: '/ventas' }
  ];

  const drawer = (
    <Box sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      pt: '64px' // Espacio para el AppBar
    }}>
      <List sx={{ flexGrow: 1, py: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
            <Tooltip title={!drawerOpen ? item.text : ''} placement="right" arrow>
              <ListItemButton 
                onClick={() => {
                  navigate(item.path);
                  // Cerrar drawer automáticamente solo en móvil
                  if (isMobile) {
                    setDrawerOpen(false);
                  }
                }}
                sx={{
                  mx: 1,
                  borderRadius: 1,
                  justifyContent: drawerOpen ? 'initial' : 'center',
                  px: drawerOpen ? 2 : 1.5,
                  '&:hover': {
                    backgroundColor: 'rgba(25, 118, 210, 0.08)',
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
              >
                <ListItemIcon sx={{ 
                  color: 'primary.main', 
                  minWidth: drawerOpen ? 40 : 'auto',
                  justifyContent: 'center'
                }}>
                  {item.icon}
                </ListItemIcon>
                {drawerOpen && (
                  <ListItemText 
                    primary={item.text}
                    sx={{
                      '& .MuiListItemText-primary': {
                        fontWeight: 500,
                        fontSize: '0.95rem'
                      }
                    }}
                  />
                )}
              </ListItemButton>
            </Tooltip>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* AppBar - Estilo YouTube: Siempre visible, por encima de todo */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: '#ffffff',
          color: '#000000',
          boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="toggle drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ 
              mr: 2,
              '&:hover': {
                backgroundColor: 'rgba(0,0,0,0.04)'
              }
            }}
          >
            <MenuIcon />
          </IconButton>
          <Typography 
            variant="h6" 
            noWrap 
            component="div" 
            sx={{ 
              flexGrow: 1,
              fontWeight: 600,
              color: 'primary.main'
            }}
          >
            Sistema de Gestión - Supermercado
          </Typography>
          <Typography variant="body2" sx={{ mr: 2, color: '#606060' }}>
            {user?.nombre}
          </Typography>
          <IconButton 
            color="inherit" 
            onClick={handleLogout}
            sx={{
              '&:hover': {
                backgroundColor: 'rgba(0,0,0,0.04)'
              }
            }}
          >
            <Logout />
          </IconButton>
        </Toolbar>
      </AppBar>
      
      {/* Drawer - Estilo YouTube: Mini drawer con iconos cuando está cerrado */}
      <Drawer
        variant={isMobile ? "temporary" : "permanent"}
        anchor="left"
        open={drawerOpen || !isMobile}
        onClose={handleDrawerToggle}
        sx={{
          width: drawerOpen ? drawerWidth : miniDrawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerOpen ? drawerWidth : miniDrawerWidth,
            boxSizing: 'border-box',
            borderRight: '1px solid rgba(0,0,0,0.12)',
            overflowX: 'hidden',
            transition: 'none',
          },
        }}
      >
        {drawer}
      </Drawer>
      
      {/* Contenido principal */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${drawerOpen ? drawerWidth : miniDrawerWidth}px)` },
          ml: { sm: 0 },
          minHeight: '100vh',
          backgroundColor: '#f9f9f9',
          transition: 'none',
        }}
      >
        <Toolbar /> {/* Espaciador para el AppBar */}
        <Box sx={{ 
          p: 3,
          width: '100%', 
          maxWidth: '100%',
          overflow: 'auto'
        }}>
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
};

export default Layout;