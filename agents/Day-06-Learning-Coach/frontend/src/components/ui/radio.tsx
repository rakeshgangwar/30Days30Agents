import React from 'react';
import { Box, BoxProps, Stack } from '@chakra-ui/react';

export interface RadioProps extends BoxProps {
  value: string;
  isChecked?: boolean;
  onChange?: (value: string) => void;
  size?: 'sm' | 'md' | 'lg';
  colorScheme?: string;
  isDisabled?: boolean;
}

export const Radio: React.FC<RadioProps> = ({
  value,
  isChecked = false,
  onChange,
  size = 'md',
  colorScheme = 'blue',
  isDisabled = false,
  children,
  ...props
}) => {
  // Get size based on size prop
  const getSize = () => {
    switch (size) {
      case 'sm':
        return { circle: '14px', dot: '6px' };
      case 'md':
        return { circle: '16px', dot: '8px' };
      case 'lg':
        return { circle: '20px', dot: '10px' };
      default:
        return { circle: '16px', dot: '8px' };
    }
  };

  const { circle, dot } = getSize();

  const handleClick = () => {
    if (!isDisabled && onChange) {
      onChange(value);
    }
  };

  return (
    <Box
      as="label"
      display="flex"
      alignItems="center"
      cursor={isDisabled ? 'not-allowed' : 'pointer'}
      opacity={isDisabled ? 0.6 : 1}
      onClick={handleClick}
      {...props}
    >
      <Box
        position="relative"
        width={circle}
        height={circle}
        borderRadius="full"
        borderWidth="2px"
        borderColor={isChecked ? `${colorScheme}.500` : 'gray.300'}
        mr={2}
      >
        {isChecked && (
          <Box
            position="absolute"
            top="50%"
            left="50%"
            transform="translate(-50%, -50%)"
            width={dot}
            height={dot}
            borderRadius="full"
            bg={`${colorScheme}.500`}
          />
        )}
      </Box>
      {children}
    </Box>
  );
};

export interface RadioGroupProps {
  value?: string;
  onChange?: (value: string) => void;
  children: React.ReactNode;
  name?: string;
  defaultValue?: string;
  size?: 'sm' | 'md' | 'lg';
  colorScheme?: string;
  isDisabled?: boolean;
}

export const RadioGroup: React.FC<RadioGroupProps> = ({
  value,
  onChange,
  children,
  name,
  defaultValue,
  size = 'md',
  colorScheme = 'blue',
  isDisabled = false,
}) => {
  const [selectedValue, setSelectedValue] = React.useState(value || defaultValue || '');

  React.useEffect(() => {
    if (value !== undefined) {
      setSelectedValue(value);
    }
  }, [value]);

  const handleChange = (newValue: string) => {
    if (!isDisabled) {
      setSelectedValue(newValue);
      if (onChange) {
        onChange(newValue);
      }
    }
  };

  // Clone children and pass props
  const clonedChildren = React.Children.map(children, (child) => {
    if (React.isValidElement(child)) {
      return React.cloneElement(child, {
        isChecked: child.props.value === selectedValue,
        onChange: handleChange,
        name,
        size,
        colorScheme,
        isDisabled,
      });
    }
    return child;
  });

  return <>{clonedChildren}</>;
};
