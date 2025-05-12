import {
  Box,
  Flex,
  Heading,
  Button,
  HStack,
  IconButton
} from '@chakra-ui/react';
import { useColorMode } from './ui/color-mode';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const navigate = useNavigate();

  return (
    <Box as="nav" bg="app.navbar" color="app.navbarText" px={4} py={3}>
      <Flex maxW="container.xl" mx="auto" alignItems="center" justifyContent="space-between">
        <Heading size="md" fontWeight="bold" cursor="pointer" onClick={() => navigate('/')}>
          Learning Coach
        </Heading>

        <HStack gap={4}>
          <Link to="/" style={{ textDecoration: 'none' }}>
            <Button variant="ghost" colorScheme="whiteAlpha" color="app.navbarText">
              Home
            </Button>
          </Link>
          <Link to="/chat" style={{ textDecoration: 'none' }}>
            <Button variant="ghost" colorScheme="whiteAlpha" color="app.navbarText">
              Chat
            </Button>
          </Link>
          <Link to="/learning-paths" style={{ textDecoration: 'none' }}>
            <Button variant="ghost" colorScheme="whiteAlpha" color="app.navbarText">
              Learning Paths
            </Button>
          </Link>
          <Link to="/resources" style={{ textDecoration: 'none' }}>
            <Button variant="ghost" colorScheme="whiteAlpha" color="app.navbarText">
              Resources
            </Button>
          </Link>
          <Link to="/quizzes" style={{ textDecoration: 'none' }}>
            <Button variant="ghost" colorScheme="whiteAlpha" color="app.navbarText">
              Quizzes
            </Button>
          </Link>
          <IconButton
            aria-label="Toggle color mode"
            variant="ghost"
            colorScheme="whiteAlpha"
            onClick={toggleColorMode}
          >
            {colorMode === 'light' ? <span>🌙</span> : <span>☀️</span>}
          </IconButton>
        </HStack>
      </Flex>
    </Box>
  );
};

export default Navbar;
