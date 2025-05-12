import {
  Box,
  Flex,
  Heading,
  Button,
  HStack,
  IconButton
} from '@chakra-ui/react';
import { useColorMode } from './ui/color-mode';
import { Link as RouterLink } from 'react-router-dom';

const Navbar = () => {
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Box as="nav" bg="blue.600" color="white" px={4} py={3}>
      <Flex maxW="container.xl" mx="auto" align="center" justify="space-between">
        <Heading as={RouterLink} to="/" size="md" fontWeight="bold">
          Learning Coach
        </Heading>

        <HStack spacing={4}>
          <Button as={RouterLink} to="/" variant="ghost" colorScheme="whiteAlpha">
            Home
          </Button>
          <Button as={RouterLink} to="/chat" variant="ghost" colorScheme="whiteAlpha">
            Chat
          </Button>
          <Button as={RouterLink} to="/learning-paths" variant="ghost" colorScheme="whiteAlpha">
            Learning Paths
          </Button>
          <Button as={RouterLink} to="/resources" variant="ghost" colorScheme="whiteAlpha">
            Resources
          </Button>
          <Button as={RouterLink} to="/quizzes" variant="ghost" colorScheme="whiteAlpha">
            Quizzes
          </Button>
          <IconButton
            aria-label="Toggle color mode"
            icon={colorMode === 'light' ? <span>🌙</span> : <span>☀️</span>}
            onClick={toggleColorMode}
            variant="ghost"
            colorScheme="whiteAlpha"
          />
        </HStack>
      </Flex>
    </Box>
  );
};

export default Navbar;
