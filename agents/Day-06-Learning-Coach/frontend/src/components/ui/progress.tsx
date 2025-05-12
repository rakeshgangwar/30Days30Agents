import React from 'react';
import { Box, BoxProps } from '@chakra-ui/react';

export interface ProgressProps extends BoxProps {
  value: number;
  max?: number;
  min?: number;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  colorScheme?: string;
  borderRadius?: string;
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  min = 0,
  size = 'md',
  colorScheme = 'blue',
  borderRadius = 'md',
  ...props
}) => {
  // Normalize value between min and max
  const normalizedValue = Math.max(min, Math.min(max, value));
  const percentage = ((normalizedValue - min) / (max - min)) * 100;

  // Get height based on size
  const getHeight = () => {
    switch (size) {
      case 'xs':
        return '0.25rem';
      case 'sm':
        return '0.5rem';
      case 'md':
        return '0.75rem';
      case 'lg':
        return '1rem';
      default:
        return '0.75rem';
    }
  };

  return (
    <Box
      position="relative"
      height={getHeight()}
      width="100%"
      bg="gray.100"
      borderRadius={borderRadius}
      overflow="hidden"
      {...props}
    >
      <Box
        position="absolute"
        top={0}
        left={0}
        height="100%"
        width={`${percentage}%`}
        bg={`${colorScheme}.500`}
        transition="width 0.3s ease"
        borderRadius={borderRadius}
      />
    </Box>
  );
};
