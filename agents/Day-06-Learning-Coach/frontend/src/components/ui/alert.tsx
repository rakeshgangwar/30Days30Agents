import React from 'react';
import { Box, Flex, Text, BoxProps } from '@chakra-ui/react';

export interface AlertProps extends BoxProps {
  status?: 'info' | 'warning' | 'success' | 'error';
  variant?: 'subtle' | 'solid' | 'left-accent' | 'top-accent';
  children: React.ReactNode;
}

export const Alert: React.FC<AlertProps> = ({
  status = 'info',
  variant = 'subtle',
  children,
  ...props
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'info':
        return 'blue';
      case 'warning':
        return 'orange';
      case 'success':
        return 'green';
      case 'error':
        return 'red';
      default:
        return 'blue';
    }
  };

  const getAlertStyles = () => {
    const color = getStatusColor();
    
    switch (variant) {
      case 'subtle':
        return {
          bg: `${color}.100`,
          color: `${color}.800`,
        };
      case 'solid':
        return {
          bg: `${color}.500`,
          color: 'white',
        };
      case 'left-accent':
        return {
          bg: `${color}.100`,
          color: `${color}.800`,
          borderLeftWidth: '4px',
          borderLeftColor: `${color}.500`,
        };
      case 'top-accent':
        return {
          bg: `${color}.100`,
          color: `${color}.800`,
          borderTopWidth: '4px',
          borderTopColor: `${color}.500`,
        };
      default:
        return {};
    }
  };

  return (
    <Box
      borderRadius="md"
      p={4}
      {...getAlertStyles()}
      {...props}
    >
      {children}
    </Box>
  );
};

export const AlertIcon: React.FC = () => {
  return (
    <Box mr={3}>
      ⓘ
    </Box>
  );
};

export const AlertTitle: React.FC<BoxProps> = ({ children, ...props }) => {
  return (
    <Text fontWeight="bold" {...props}>
      {children}
    </Text>
  );
};

export const AlertDescription: React.FC<BoxProps> = ({ children, ...props }) => {
  return (
    <Text {...props}>
      {children}
    </Text>
  );
};
