import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  CircularProgress, 
  TextField, 
  Typography, 
  Alert 
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { useAppContext } from '../../contexts/AppContext';
import api from '../../services/api';

const QueryInput: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const [query, setQuery] = useState('');
  const [error, setError] = useState<string | null>(null);
  
  const isCSVActive = state.dataSource === 'csv' && state.csv.fileId;
  const isDatabaseActive = state.dataSource === 'database' && state.database.connected;
  const isActive = isCSVActive || isDatabaseActive;
  
  const handleQueryChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(event.target.value);
    dispatch({ type: 'SET_QUERY', payload: event.target.value });
  };
  
  const handleSubmit = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }
    
    setError(null);
    dispatch({ type: 'SET_QUERY_LOADING', payload: true });
    
    try {
      let response;
      
      if (isCSVActive && state.csv.fileId) {
        response = await api.queryCSV(state.csv.fileId, query);
      } else if (isDatabaseActive && state.database.connectionId) {
        response = await api.queryDatabase(state.database.connectionId, { query });
      } else {
        throw new Error('No active data source');
      }
      
      const data = response.data;
      
      if (data.success && data.result) {
        dispatch({ type: 'SET_QUERY_RESULT', payload: data.result });
      } else {
        dispatch({ 
          type: 'SET_QUERY_ERROR', 
          payload: data.error || 'Failed to process query' 
        });
      }
    } catch (err) {
      console.error('Error processing query:', err);
      dispatch({ 
        type: 'SET_QUERY_ERROR', 
        payload: 'Error processing query. Please try again.' 
      });
    }
  };
  
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && event.ctrlKey) {
      handleSubmit();
    }
  };
  
  return (
    <Card variant="outlined" sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Natural Language Query
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {!isActive && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Please select and connect to a data source first
          </Alert>
        )}
        
        <TextField
          fullWidth
          multiline
          rows={3}
          label="Enter your query in natural language"
          placeholder="Example: Show me the average sales by region as a bar chart"
          value={query}
          onChange={handleQueryChange}
          onKeyDown={handleKeyDown}
          disabled={!isActive}
          sx={{ mb: 2 }}
        />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="caption" color="text.secondary">
            Press Ctrl+Enter to submit
          </Typography>
          
          <Button
            variant="contained"
            color="primary"
            endIcon={state.query.loading ? <CircularProgress size={20} color="inherit" /> : <SendIcon />}
            onClick={handleSubmit}
            disabled={!isActive || !query.trim() || state.query.loading}
          >
            {state.query.loading ? 'Processing...' : 'Submit Query'}
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default QueryInput;
