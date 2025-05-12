import { Box, Heading, Text, Container } from '@chakra-ui/react';
import ChatInterface from '../components/ChatInterface';

const ChatPage = () => {
  return (
    <Container maxW="container.lg" py={8}>
      <Box textAlign="center" mb={8}>
        <Heading as="h1" size="xl" mb={4}>
          Chat with Learning Coach
        </Heading>
        <Text fontSize="lg" color="gray.600">
          Ask questions, get learning recommendations, or create a personalized learning path
        </Text>
      </Box>
      
      <ChatInterface />
    </Container>
  );
};

export default ChatPage;
