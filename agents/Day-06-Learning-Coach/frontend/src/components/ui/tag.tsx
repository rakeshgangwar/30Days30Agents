import React from 'react';
import { Box, BoxProps, Flex } from '@chakra-ui/react';

export interface TagProps extends BoxProps {
  size?: 'sm' | 'md' | 'lg';
  variant?: 'solid' | 'subtle' | 'outline';
  colorScheme?: string;
}

export const Tag: React.FC<TagProps> = ({
  size = 'md',
  variant = 'subtle',
  colorScheme = 'gray',
  children,
  ...props
}) => {
  // Get size based on size prop
  const getSize = () => {
    switch (size) {
      case 'sm':
        return { px: '0.5rem', py: '0.125rem', fontSize: '0.75rem' };
      case 'md':
        return { px: '0.75rem', py: '0.25rem', fontSize: '0.875rem' };
      case 'lg':
        return { px: '1rem', py: '0.375rem', fontSize: '1rem' };
      default:
        return { px: '0.75rem', py: '0.25rem', fontSize: '0.875rem' };
    }
  };

  // Get variant styles
  const getVariantStyles = () => {
    switch (variant) {
      case 'solid':
        return {
          bg: `${colorScheme}.500`,
          color: 'white',
        };
      case 'subtle':
        return {
          bg: `${colorScheme}.100`,
          color: `${colorScheme}.800`,
        };
      case 'outline':
        return {
          bg: 'transparent',
          color: `${colorScheme}.500`,
          border: '1px solid',
          borderColor: `${colorScheme}.500`,
        };
      default:
        return {
          bg: `${colorScheme}.100`,
          color: `${colorScheme}.800`,
        };
    }
  };

  const sizeStyles = getSize();
  const variantStyles = getVariantStyles();

  return (
    <Flex
      display="inline-flex"
      alignItems="center"
      borderRadius="md"
      fontWeight="medium"
      whiteSpace="nowrap"
      verticalAlign="middle"
      {...sizeStyles}
      {...variantStyles}
      {...props}
    >
      {children}
    </Flex>
  );
};
