import { Box, Heading, Text, Button, VStack, SimpleGrid, Card as CardNamespace } from '@chakra-ui/react';

const HomePage = () => {
  return (
    <Box>
      <VStack gap={8} textAlign="center" mb={12}>
        <Heading as="h1" size="2xl" color="app.pageTitleColor">
          Welcome to Learning Coach
        </Heading>
        <Text fontSize="xl" maxW="container.md" color="app.textColor">
          Your AI-powered learning assistant that creates personalized learning paths, tracks progress,
          generates quizzes, and discovers relevant educational resources.
        </Text>
        <Button size="lg" colorScheme="brand" onClick={() => window.location.href = '/chat'}>
          Chat with Learning Coach
        </Button>
      </VStack>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} gap={8}>
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
    <CardNamespace.Root bg="app.cardBg" borderColor="app.cardBorder" borderWidth="1px">
      <CardNamespace.Header>
        <Heading size="md" color="app.headingColor">{title}</Heading>
      </CardNamespace.Header>
      <CardNamespace.Body>
        <Text color="app.textColor">{description}</Text>
      </CardNamespace.Body>
    </CardNamespace.Root>
  );
};

export default HomePage;
