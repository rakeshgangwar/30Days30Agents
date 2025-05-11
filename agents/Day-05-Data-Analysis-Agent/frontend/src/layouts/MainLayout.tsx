import React, { ReactNode } from 'react';
import { 
  AppBar, 
  Box, 
  Container, 
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
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <CssBaseline />
      
      {/* App Bar */}
      <AppBar position="static">
        <Toolbar>
          <BarChartIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Data Analysis Agent
          </Typography>
        </Toolbar>
      </AppBar>
      
      {/* Main Content */}
      <Container 
        component="main" 
        maxWidth="lg" 
        sx={{ 
          mt: 4, 
          mb: 4,
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {children}
      </Container>
      
      {/* Footer */}
      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          backgroundColor: theme.palette.grey[100],
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="body2" color="text.secondary" align="center">
            Data Analysis Agent - 30 Days 30 Agents
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};

export default MainLayout;
