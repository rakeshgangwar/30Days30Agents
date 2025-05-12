import { Box, Heading, Text, Button, VStack } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

const NotFoundPage = () => {
  return (
    <Box textAlign="center" py={10}>
      <VStack spacing={6}>
        <Heading as="h1" size="2xl">
          404
        </Heading>
        <Text fontSize="xl">Page not found</Text>
        <Text>The page you're looking for does not exist or has been moved.</Text>
        <Button as={RouterLink} to="/" colorScheme="blue">
          Return to Home
        </Button>
      </VStack>
    </Box>
  );
};

export default NotFoundPage;
