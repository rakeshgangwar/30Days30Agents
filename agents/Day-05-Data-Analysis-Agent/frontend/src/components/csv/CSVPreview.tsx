import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow, 
  Paper 
} from '@mui/material';
import { useAppContext } from '../../contexts/AppContext';

const CSVPreview: React.FC = () => {
  const { state } = useAppContext();
  const { preview, columns } = state.csv;
  
  if (!preview.length || !columns.length) {
    return null;
  }
  
  return (
    <Card variant="outlined" sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          CSV Preview
        </Typography>
        
        <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 300 }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                {columns.map((column) => (
                  <TableCell key={column}>
                    <Typography variant="subtitle2">{column}</Typography>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {preview.map((row, rowIndex) => (
                <TableRow key={rowIndex}>
                  {columns.map((column) => (
                    <TableCell key={`${rowIndex}-${column}`}>
                      {row[column] !== undefined ? String(row[column]) : ''}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        <Box sx={{ mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Showing {preview.length} of {state.csv.rows} rows
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default CSVPreview;
