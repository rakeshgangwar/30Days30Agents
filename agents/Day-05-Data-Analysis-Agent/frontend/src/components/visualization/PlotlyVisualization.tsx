import React, { useEffect, useState } from 'react';
import { Box, Paper, Typography, CircularProgress } from '@mui/material';
import Plot from 'react-plotly.js';
import type { VisualizationData } from '../../types/index';

interface PlotlyVisualizationProps {
  data: VisualizationData;
}

const PlotlyVisualization: React.FC<PlotlyVisualizationProps> = ({ data }) => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Log the visualization data for debugging
    console.log('Visualization data received:', data);

    if (data && data.figure) {
      console.log('Figure data:', data.figure);
      console.log('Figure data keys:', Object.keys(data.figure));

      if (data.figure.data) {
        console.log('Plot data traces:', data.figure.data.length);
      }

      if (data.figure.layout) {
        console.log('Layout:', data.figure.layout);
      }

      setIsLoading(false);
    } else {
      console.error('Invalid visualization data received');
      setError('Invalid visualization data structure');
      setIsLoading(false);
    }
  }, [data]);

  if (isLoading) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <CircularProgress />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Loading visualization...
        </Typography>
      </Box>
    );
  }

  if (error || !data || !data.figure) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          {error || 'No visualization data available'}
        </Typography>
      </Box>
    );
  }

  // Extract the figure data from the visualization
  const { figure } = data;

  // Default layout options
  const defaultLayout = {
    autosize: true,
    margin: { l: 50, r: 50, t: 50, b: 50 },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: {
      family: 'Arial, sans-serif'
    },
    height: 500,  // Set a fixed height
    width: 800    // Set a fixed width that will be responsive
  };

  // Merge the provided layout with default options
  const layout = {
    ...defaultLayout,
    ...(figure.layout || {})
  };

  // Ensure we have valid data
  const plotData = Array.isArray(figure.data) ? figure.data : [];

  // Log the final data being passed to Plot
  console.log('Final plot data:', plotData);
  console.log('Final layout:', layout);

  return (
    <Box
      sx={{
        width: '100%',
        height: { xs: '400px', sm: '500px', md: '600px' },
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center'
      }}
    >
      <Plot
        data={plotData}
        layout={layout}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler={true}
        config={{
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: [
            'sendDataToCloud',
            'lasso2d',
            'select2d'
          ]
        }}
      />
    </Box>
  );
};

export default PlotlyVisualization;
