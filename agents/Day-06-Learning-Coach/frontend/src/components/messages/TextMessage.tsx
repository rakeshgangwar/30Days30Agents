import { Box } from '@chakra-ui/react';
import ReactMarkdown from 'react-markdown';
import { useColorModeValue } from '../ui/color-mode';

interface TextMessageProps {
  content: string;
}

const TextMessage = ({ content }: TextMessageProps) => {
  const bgColor = useColorModeValue('white', 'gray.700');
  const textColor = useColorModeValue('gray.800', 'gray.100');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const codeBackground = useColorModeValue('gray.50', 'gray.800');
  const codeBorderColor = useColorModeValue('gray.200', 'gray.600');

  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      overflow="hidden"
      p={4}
      bg={bgColor}
      boxShadow="sm"
      w="100%"
      color={textColor}
      sx={{
        '.markdown-content pre': {
          backgroundColor: codeBackground,
          borderColor: codeBorderColor,
          borderWidth: '1px',
          borderRadius: 'md',
        },
        '.markdown-content code': {
          backgroundColor: codeBackground,
          borderColor: codeBorderColor,
          borderWidth: '1px',
          borderRadius: 'sm',
          px: 1,
        },
        '.markdown-content pre code': {
          backgroundColor: 'transparent',
          borderWidth: 0,
          p: 0,
        },
        '.markdown-content blockquote': {
          borderLeftColor: borderColor,
        },
        '.markdown-content a': {
          color: useColorModeValue('blue.600', 'blue.300'),
        },
        '.markdown-content table th': {
          backgroundColor: codeBackground,
        },
        '.markdown-content table th, .markdown-content table td': {
          borderColor: borderColor,
        }
      }}
    >
      <Box className="markdown-content">
        <ReactMarkdown>{content}</ReactMarkdown>
      </Box>
    </Box>
  );
};

export default TextMessage;
