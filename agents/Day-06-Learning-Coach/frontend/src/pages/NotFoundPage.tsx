import { Box, Heading, Text, Button, VStack } from '@chakra-ui/react';
import { Link } from 'react-router-dom';

const NotFoundPage = () => {
  return (
    <Box textAlign="center" py={10}>
      <VStack gap={6}>
        <Heading as="h1" size="2xl" color="app.headingColor">
          404
        </Heading>
        <Text fontSize="xl" color="app.textColor">Page not found</Text>
        <Text color="app.mutedText">The page you're looking for does not exist or has been moved.</Text>
        <Link to="/" style={{ textDecoration: 'none' }}>
          <Button colorScheme="brand">
            Return to Home
          </Button>
        </Link>
      </VStack>
    </Box>
  );
};

export default NotFoundPage;
