import { Box, Text } from '@chakra-ui/react';

interface TextMessageProps {
  content: string;
}

const TextMessage = ({ content }: TextMessageProps) => {
  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      overflow="hidden"
      p={4}
      bg="white"
      boxShadow="sm"
      w="100%"
    >
      <Text whiteSpace="pre-wrap">{content}</Text>
    </Box>
  );
};

export default TextMessage;
