import React from 'react';
import { Box, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { AppProvider } from './contexts/AppContext';
import MainLayout from './layouts/MainLayout';
import DataSourceSelection from './components/DataSourceSelection';
import CSVUpload from './components/csv/CSVUpload';
import CSVPreview from './components/csv/CSVPreview';
import DBConnection from './components/db/DBConnection';
import QueryInput from './components/query/QueryInput';
import ResultsDisplay from './components/results/ResultsDisplay';
import { useAppContext } from './contexts/AppContext';

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

// Content component that uses the app context
const AppContent: React.FC = () => {
  const { state } = useAppContext();

  return (
    <Box>
      <DataSourceSelection />

      {state.dataSource === 'csv' && (
        <>
          <CSVUpload />
          <CSVPreview />
        </>
      )}

      {state.dataSource === 'database' && (
        <DBConnection />
      )}

      {state.dataSource && (
        <>
          <QueryInput />
          <ResultsDisplay />
        </>
      )}
    </Box>
  );
};

// Main App component
function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppProvider>
        <MainLayout>
          <AppContent />
        </MainLayout>
      </AppProvider>
    </ThemeProvider>
  );
}

export default App;
