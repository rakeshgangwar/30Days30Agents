import { Box, Heading, Text, Button, VStack, SimpleGrid, Card as CardNamespace, Icon } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

const HomePage = () => {
  return (
    <Box>
      <VStack spacing={8} textAlign="center" mb={12}>
        <Heading as="h1" size="2xl">
          Welcome to Learning Coach
        </Heading>
        <Text fontSize="xl" maxW="container.md">
          Your AI-powered learning assistant that creates personalized learning paths, tracks progress,
          generates quizzes, and discovers relevant educational resources.
        </Text>
        <Button as={RouterLink} to="/chat" colorScheme="blue" size="lg">
          Chat with Learning Coach
        </Button>
      </VStack>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={8}>
        <FeatureCard
          title="Personalized Learning Paths"
          description="Create customized learning journeys based on your goals and interests."
        />
        <FeatureCard
          title="Progress Tracking"
          description="Monitor your learning progress and stay motivated with visual analytics."
        />
        <FeatureCard
          title="Interactive Quizzes"
          description="Test your knowledge with adaptive quizzes that focus on your weak areas."
        />
        <FeatureCard
          title="Resource Discovery"
          description="Find high-quality learning resources from trusted sources."
        />
      </SimpleGrid>
    </Box>
  );
};

const FeatureCard = ({ title, description }: { title: string; description: string }) => {
  return (
    <CardNamespace.Root>
      <CardNamespace.Header>
        <Heading size="md">{title}</Heading>
      </CardNamespace.Header>
      <CardNamespace.Body>
        <Text>{description}</Text>
      </CardNamespace.Body>
    </CardNamespace.Root>
  );
};

export default HomePage;
