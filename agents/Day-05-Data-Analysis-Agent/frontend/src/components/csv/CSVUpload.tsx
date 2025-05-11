import React, { useState, useRef } from 'react';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  CircularProgress, 
  Typography, 
  Alert 
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { useAppContext } from '../../contexts/AppContext';
import api from '../../services/api';

const CSVUpload: React.FC = () => {
  const { state, dispatch } = useAppContext();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    // Check if file is a CSV
    if (!file.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.uploadCSV(file);
      const data = response.data;
      
      if (data.success) {
        dispatch({ 
          type: 'SET_CSV_DATA', 
          payload: {
            fileId: file.name, // Using filename as ID for simplicity
            fileName: file.name,
            columns: data.columns || [],
            rows: data.rows || 0,
            preview: data.preview || [],
          }
        });
      } else {
        setError(data.error || 'Failed to upload CSV file');
      }
    } catch (err) {
      console.error('Error uploading CSV:', err);
      setError('Error uploading CSV file. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };
  
  const handleReset = () => {
    dispatch({ type: 'RESET_CSV_DATA' });
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  return (
    <Card variant="outlined" sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          CSV Data Source
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {state.csv.fileId ? (
          <Box>
            <Alert severity="success" sx={{ mb: 2 }}>
              Successfully uploaded: {state.csv.fileName}
            </Alert>
            
            <Typography variant="body2" gutterBottom>
              Rows: {state.csv.rows} | Columns: {state.csv.columns.length}
            </Typography>
            
            <Box sx={{ mt: 2 }}>
              <Button 
                variant="outlined" 
                color="primary" 
                onClick={handleReset}
                sx={{ mr: 1 }}
              >
                Upload Different File
              </Button>
            </Box>
          </Box>
        ) : (
          <Box 
            sx={{ 
              border: '2px dashed #ccc', 
              borderRadius: 2, 
              p: 3, 
              textAlign: 'center',
              cursor: 'pointer',
              '&:hover': {
                borderColor: 'primary.main',
              },
            }}
            onClick={handleUploadClick}
          >
            <input
              type="file"
              accept=".csv"
              hidden
              ref={fileInputRef}
              onChange={handleFileChange}
            />
            
            <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            
            <Typography variant="h6" gutterBottom>
              Upload CSV File
            </Typography>
            
            <Typography variant="body2" color="textSecondary">
              Click to browse or drag and drop
            </Typography>
            
            {loading && (
              <CircularProgress size={24} sx={{ mt: 2 }} />
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default CSVUpload;
