import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  ToggleButtonGroup,
  ToggleButton
} from '@mui/material';
import TableChartIcon from '@mui/icons-material/TableChart';
import StorageIcon from '@mui/icons-material/Storage';
import { useAppContext } from '../contexts/AppContext';
import type { DataSourceType } from '../types/index';

const DataSourceSelection: React.FC = () => {
  const { state, dispatch } = useAppContext();

  const handleDataSourceChange = (
    event: React.MouseEvent<HTMLElement>,
    newDataSource: DataSourceType
  ) => {
    if (newDataSource !== null) {
      dispatch({ type: 'SET_DATA_SOURCE', payload: newDataSource });
    }
  };

  return (
    <Card variant="outlined" sx={{ mb: 3, width: '100%' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Select Data Source
        </Typography>

        <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
          <ToggleButtonGroup
            value={state.dataSource}
            exclusive
            onChange={handleDataSourceChange}
            aria-label="data source selection"
            size="large"
            color="primary"
          >
            <ToggleButton value="csv" aria-label="CSV file">
              <TableChartIcon sx={{ mr: 1 }} />
              CSV File
            </ToggleButton>
            <ToggleButton value="database" aria-label="Database">
              <StorageIcon sx={{ mr: 1 }} />
              Database
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>

        <Typography variant="body2" color="text.secondary" align="center">
          {state.dataSource === 'csv'
            ? 'Upload a CSV file to analyze data with natural language queries'
            : state.dataSource === 'database'
              ? 'Connect to a database to analyze data with natural language queries'
              : 'Choose a data source to get started'}
        </Typography>
      </CardContent>
    </Card>
  );
};

export default DataSourceSelection;
