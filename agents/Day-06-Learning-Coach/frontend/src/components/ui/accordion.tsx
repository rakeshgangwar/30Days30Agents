import React from 'react';
import {
  Box,
  Flex,
  Stack,
  Text,
  BoxProps
} from '@chakra-ui/react';

// Custom Divider component
export const Divider: React.FC<BoxProps> = (props) => {
  return (
    <Box
      as="hr"
      borderBottomWidth="1px"
      borderColor="gray.200"
      my={4}
      {...props}
    />
  );
};

export interface AccordionItemProps {
  title: React.ReactNode;
  children: React.ReactNode;
  isOpen?: boolean;
  onToggle?: () => void;
}

export const AccordionItem: React.FC<AccordionItemProps> = ({
  title,
  children,
  isOpen = false,
  onToggle
}) => {
  const [isExpanded, setIsExpanded] = React.useState(isOpen);

  const handleToggle = () => {
    const newState = !isExpanded;
    setIsExpanded(newState);
    if (onToggle) onToggle();
  };

  return (
    <Box borderWidth="1px" borderRadius="md" mb={2}>
      <Flex
        as="button"
        onClick={handleToggle}
        width="100%"
        p={3}
        justifyContent="space-between"
        alignItems="center"
        bg={isExpanded ? "gray.100" : "white"}
        _hover={{ bg: "gray.50" }}
        borderBottomWidth={isExpanded ? "1px" : "0"}
      >
        <Text fontWeight="medium">{title}</Text>
        <Box
          transform={isExpanded ? "rotate(180deg)" : "rotate(0deg)"}
          transition="transform 0.2s"
        >
          ▼
        </Box>
      </Flex>
      {isExpanded && (
        <Box p={4}>
          {children}
        </Box>
      )}
    </Box>
  );
};

export interface AccordionProps {
  children: React.ReactNode;
  defaultIndex?: number[];
  allowMultiple?: boolean;
}

export const Accordion: React.FC<AccordionProps> = ({
  children
}) => {
  return (
    <Stack direction="column" gap={0} width="100%">
      {children}
    </Stack>
  );
};

export const AccordionButton: React.FC<BoxProps> = (props) => {
  return <Box as="button" {...props} />;
};

export const AccordionPanel: React.FC<BoxProps> = (props) => {
  return <Box {...props} />;
};

export const AccordionIcon: React.FC = () => {
  return <Box as="span">▼</Box>;
};
