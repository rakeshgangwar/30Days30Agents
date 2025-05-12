import React from 'react';
import { Box, BoxProps } from '@chakra-ui/react';

export interface CardProps extends BoxProps {
  variant?: 'outline' | 'filled' | 'elevated';
}

export const Card: React.FC<CardProps> = ({ 
  variant = 'outline', 
  children, 
  ...props 
}) => {
  const getCardStyle = () => {
    switch (variant) {
      case 'outline':
        return {
          borderWidth: '1px',
          borderRadius: 'md',
        };
      case 'filled':
        return {
          bg: 'gray.100',
          borderRadius: 'md',
        };
      case 'elevated':
        return {
          boxShadow: 'md',
          borderRadius: 'md',
        };
      default:
        return {};
    }
  };

  return (
    <Box {...getCardStyle()} overflow="hidden" {...props}>
      {children}
    </Box>
  );
};

export const CardHeader: React.FC<BoxProps> = ({ children, ...props }) => {
  return (
    <Box p={4} pb={2} {...props}>
      {children}
    </Box>
  );
};

export const CardBody: React.FC<BoxProps> = ({ children, ...props }) => {
  return (
    <Box p={4} pt={2} pb={2} {...props}>
      {children}
    </Box>
  );
};

export const CardFooter: React.FC<BoxProps> = ({ children, ...props }) => {
  return (
    <Box p={4} pt={2} {...props}>
      {children}
    </Box>
  );
};
