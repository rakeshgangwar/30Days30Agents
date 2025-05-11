import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  Divider,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab
} from '@mui/material';
import { useAppContext } from '../../contexts/AppContext';
import PlotlyVisualization from '../visualization/PlotlyVisualization';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`results-tabpanel-${index}`}
      aria-labelledby={`results-tab-${index}`}
      style={{ width: '100%' }}
    >
      {value === index && (
        <Box sx={{ p: 2, width: '100%' }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const ResultsDisplay: React.FC = () => {
  const { state } = useAppContext();
  const { result, error, loading } = state.query;
  const [tabValue, setTabValue] = React.useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Card variant="outlined" sx={{ width: '100%' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Processing Query...
          </Typography>
          <Alert severity="info" sx={{ width: '100%' }}>
            The AI is analyzing your data. This may take a few moments.
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card variant="outlined" sx={{ width: '100%' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Error
          </Typography>
          <Alert severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!result) {
    return null;
  }

  // Log the result for debugging
  console.log('Query result:', result);

  const hasVisualization = result.visualization && result.visualization.figure;
  const hasData = result.data && result.data.length > 0;
  const hasCode = result.code && result.code.trim().length > 0;

  // Log visualization data if available
  if (hasVisualization) {
    console.log('Visualization data available:', result.visualization);
  } else {
    console.log('No visualization data in result');
  }

  return (
    <Card variant="outlined" sx={{ width: '100%' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Analysis Results
        </Typography>

        <Box sx={{ borderBottom: 1, borderColor: 'divider', width: '100%' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="results tabs" variant="scrollable" scrollButtons="auto" sx={{ width: '100%' }}>
            <Tab label="Analysis" id="results-tab-0" aria-controls="results-tabpanel-0" />
            {hasData && (
              <Tab label="Data" id="results-tab-1" aria-controls="results-tabpanel-1" />
            )}
            {hasVisualization && (
              <Tab label="Visualization" id="results-tab-2" aria-controls="results-tabpanel-2" />
            )}
            {hasCode && (
              <Tab label="Code" id="results-tab-3" aria-controls="results-tabpanel-3" />
            )}
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-wrap', width: '100%' }}>
            {result.text}
          </Typography>
        </TabPanel>

        {hasData && (
          <TabPanel value={tabValue} index={1}>
            <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: { xs: 300, sm: 400, md: 500 }, width: '100%' }}>
              <Table stickyHeader size="small">
                <TableHead>
                  <TableRow>
                    {Object.keys(result.data[0]).map((key) => (
                      <TableCell key={key}>
                        <Typography variant="subtitle2">{key}</Typography>
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {result.data.map((row, rowIndex) => (
                    <TableRow key={rowIndex}>
                      {Object.entries(row).map(([key, value]) => (
                        <TableCell key={`${rowIndex}-${key}`}>
                          {value !== null && value !== undefined ? String(value) : ''}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>
        )}

        {hasVisualization && (
          <TabPanel value={tabValue} index={hasData ? 2 : 1}>
            <Box sx={{ width: '100%' }}>
              <Typography variant="subtitle1" gutterBottom>
                Visualization
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                The visualization is based on the query results. You can interact with the chart using the toolbar.
              </Typography>
              <PlotlyVisualization data={result.visualization} />
            </Box>
          </TabPanel>
        )}

        {hasCode && (
          <TabPanel value={tabValue} index={(hasData ? 1 : 0) + (hasVisualization ? 1 : 0) + 1}>
            <Paper
              variant="outlined"
              sx={{
                p: 2,
                backgroundColor: '#f5f5f5',
                fontFamily: 'monospace',
                whiteSpace: 'pre-wrap',
                overflowX: 'auto',
                width: '100%'
              }}
            >
              {result.code}
            </Paper>
          </TabPanel>
        )}
      </CardContent>
    </Card>
  );
};

export default ResultsDisplay;
