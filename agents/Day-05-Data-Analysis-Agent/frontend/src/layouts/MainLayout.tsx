import React from 'react';
import type { ReactNode } from 'react';
import {
  AppBar,
  Box,
  CssBaseline,
  Toolbar,
  Typography,
  useTheme
} from '@mui/material';
import BarChartIcon from '@mui/icons-material/BarChart';

interface MainLayoutProps {
  children: ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const theme = useTheme();

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', width: '100vw', maxWidth: '100%' }}>
      <CssBaseline />

      {/* App Bar */}
      <AppBar position="static" sx={{ width: '100%' }}>
        <Toolbar>
          <BarChartIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Data Analysis Agent
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          mt: 4,
          mb: 4,
          px: { xs: 2, sm: 3, md: 4 },
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          width: '100%',
          maxWidth: '100%'
        }}
      >
        {children}
      </Box>

      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 3,
          px: { xs: 2, sm: 3, md: 4 },
          mt: 'auto',
          backgroundColor: theme.palette.grey[100],
        }}
      >
        <Typography variant="body2" color="text.secondary" align="center">
          Data Analysis Agent - 30 Days 30 Agents
        </Typography>
      </Box>
    </Box>
  );
};

export default MainLayout;
