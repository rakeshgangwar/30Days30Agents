import React from 'react';
import { Box, Paper, Typography } from '@mui/material';
import Plot from 'react-plotly.js';
import type { VisualizationData } from '../../types/index';

interface PlotlyVisualizationProps {
  data: VisualizationData;
}

const PlotlyVisualization: React.FC<PlotlyVisualizationProps> = ({ data }) => {
  if (!data || !data.figure) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No visualization data available
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
    }
  };

  // Merge the provided layout with default options
  const layout = {
    ...defaultLayout,
    ...(figure.layout || {})
  };

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
        data={figure.data || []}
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
