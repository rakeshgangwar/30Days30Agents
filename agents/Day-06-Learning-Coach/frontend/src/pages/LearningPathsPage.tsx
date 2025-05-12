import { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Heading,
  Text,
  Container,
  SimpleGrid,
  Card,
  Button,
  Badge,
  Flex,
  Alert,
  Spinner,
  Tag,
  HStack,
  Icon,
} from '@chakra-ui/react';

import { FiClock } from 'react-icons/fi';

interface LearningPathTopic {
  name: string;
  order: number;
}

interface LearningPath {
  id: string;
  title: string;
  description: string;
  topics: LearningPathTopic[];
  user_id: string;
  created_at: string;
  progress: {
    completed_topics: number;
    total_topics: number;
  };
}

const LearningPathsPage = () => {
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Use semantic tokens from theme
  const cardBg = "app.cardBg";
  const borderColor = "app.cardBorder";

  useEffect(() => {
    const fetchLearningPaths = async () => {
      try {
        // Fetch learning paths from the API
        const response = await fetch('/api/v1/paths');

        if (!response.ok) {
          throw new Error('Failed to fetch learning paths');
        }

        const data = await response.json();

        // Check if we got data back
        if (data && Array.isArray(data)) {
          console.log('Fetched learning paths:', data);
          setLearningPaths(data);
        } else {
          console.warn('Received invalid data format for learning paths:', data);
          setError('Received invalid data format from the server.');
          setLearningPaths([]);
        }
      } catch (err) {
        console.error('Error fetching learning paths:', err);
        setError('Failed to load learning paths. Please try again later.');
        setLearningPaths([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLearningPaths();
  }, []);

  if (isLoading) {
    return (
      <Container maxW="container.lg" py={8}>
        <Flex justify="center" align="center" minH="50vh">
          <Spinner size="xl" />
        </Flex>
      </Container>
    );
  }

  return (
    <Container maxW="container.lg" py={8}>
      <Box textAlign="center" mb={8}>
        <Heading as="h1" size="xl" mb={4} color="app.pageTitleColor">
          Learning Paths
        </Heading>
        <Text fontSize="lg" color="app.textColor">
          Your personalized learning journeys
        </Text>
      </Box>

      {error && (
        <Alert.Root status="error" mb={6} borderRadius="md">
          <Alert.Indicator />
          <Alert.Title>Error!</Alert.Title>
          <Alert.Description>{error}</Alert.Description>
        </Alert.Root>

      )}

      {learningPaths.length === 0 ? (
        <Box textAlign="center" p={8} borderWidth="1px" borderRadius="lg">
          <Text mb={4}>You don't have any learning paths yet.</Text>
          <Button colorScheme="blue" asChild>
            <RouterLink to="/chat">Chat with Learning Coach to create one</RouterLink>
          </Button>
        </Box>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2 }} gap={6}>
          {learningPaths.map((path) => (
            <Card.Root key={path.id} bg={cardBg} borderColor={borderColor} borderWidth="1px" borderRadius="lg" overflow="hidden">
              <Card.Header>
                <Heading size="md" color="app.headingColor">{path.title}</Heading>
              </Card.Header>
              <Card.Body>
                <Text mb={4}>{path.description}</Text>
                <HStack mb={2}>
                  <Tag.Root size="sm" colorScheme="blue">
                    <Tag.Label>
                      <Icon as={FiClock} mr={1} />
                      {path.topics.length} topics
                    </Tag.Label>
                  </Tag.Root>
                  <Tag.Root size="sm" colorScheme="green">
                    <Tag.Label>
                      {Math.round((path.progress.completed_topics / path.progress.total_topics) * 100)}% complete
                    </Tag.Label>
                  </Tag.Root>
                </HStack>
                <Box mt={4}>
                  <Text fontWeight="medium" mb={2}>Topics:</Text>
                  {path.topics.map((topic, index) => (
                    <Flex key={index} align="center" mb={1}>
                      <Badge mr={2} colorScheme="blue">{topic.order}</Badge>
                      <Text>{topic.name}</Text>
                    </Flex>
                  ))}
                </Box>
              </Card.Body>
              <Card.Footer>
                <Button
                  colorScheme="blue"
                  size="sm"
                  width="full"
                  asChild
                >
                  <RouterLink to={`/learning-paths/${path.id}`}>
                    Continue Learning
                  </RouterLink>
                </Button>
              </Card.Footer>
            </Card.Root>
          ))}
        </SimpleGrid>
      )}
    </Container>
  );
};

export default LearningPathsPage;
