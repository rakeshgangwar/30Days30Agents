import { useState, useEffect } from 'react';
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
  Spinner,
  Alert,
  Tag,
  HStack,
  Progress,
} from '@chakra-ui/react';
import { useColorModeValue } from '../components/ui/color-mode';
import { FiClock } from 'react-icons/fi';

interface Quiz {
  id: string;
  title: string;
  description: string;
  topic: string;
  difficulty: string;
  question_count: number;
  estimated_time_minutes: number;
  created_at: string;
  last_attempt?: {
    date: string;
    score: number;
    completed: boolean;
  };
}

const QuizzesPage = () => {
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    const fetchQuizzes = async () => {
      try {
        // Replace with actual API call when backend is ready
        const response = await fetch('/api/v1/quizzes');

        if (!response.ok) {
          throw new Error('Failed to fetch quizzes');
        }

        const data = await response.json();
        setQuizzes(data);
      } catch (err) {
        console.error('Error fetching quizzes:', err);
        setError('Failed to load quizzes. Please try again later.');

        // For development: mock data until backend is ready
        setQuizzes([
          {
            id: '1',
            title: 'Python Basics Quiz',
            description: 'Test your knowledge of Python fundamentals',
            topic: 'Python',
            difficulty: 'beginner',
            question_count: 10,
            estimated_time_minutes: 15,
            created_at: new Date().toISOString(),
            last_attempt: {
              date: new Date(Date.now() - 86400000).toISOString(), // yesterday
              score: 80,
              completed: true
            }
          },
          {
            id: '2',
            title: 'HTML and CSS Fundamentals',
            description: 'Test your understanding of HTML and CSS basics',
            topic: 'Web Development',
            difficulty: 'beginner',
            question_count: 15,
            estimated_time_minutes: 20,
            created_at: new Date().toISOString(),
            last_attempt: {
              date: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
              score: 60,
              completed: true
            }
          },
          {
            id: '3',
            title: 'JavaScript Advanced Concepts',
            description: 'Challenge yourself with advanced JavaScript topics',
            topic: 'JavaScript',
            difficulty: 'advanced',
            question_count: 12,
            estimated_time_minutes: 25,
            created_at: new Date().toISOString()
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchQuizzes();
  }, []);

  // Function to get color based on difficulty
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'beginner':
        return 'green';
      case 'intermediate':
        return 'blue';
      case 'advanced':
        return 'purple';
      case 'expert':
        return 'red';
      default:
        return 'gray';
    }
  };

  // Function to get color based on score
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'yellow';
    return 'red';
  };

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
        <Heading as="h1" size="xl" mb={4}>
          Quizzes
        </Heading>
        <Text fontSize="lg" color="gray.600">
          Test your knowledge and track your progress
        </Text>
      </Box>

      {error && (
        <Alert.Root status="error" mb={6} borderRadius="md">
          <Alert.Indicator />
          <Alert.Title>Error!</Alert.Title>
          <Alert.Description>{error}</Alert.Description>
        </Alert.Root>
      )}

      {quizzes.length === 0 ? (
        <Box textAlign="center" p={8} borderWidth="1px" borderRadius="lg">
          <Text mb={4}>No quizzes available yet.</Text>
          <Button colorScheme="blue" asChild>
            <a href="/chat">Chat with Learning Coach to create one</a>
          </Button>
        </Box>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2 }} gap={6}>
          {quizzes.map((quiz) => (
            <Card.Root key={quiz.id} bg={cardBg} borderColor={borderColor} borderWidth="1px" borderRadius="lg" overflow="hidden">
              <Card.Header>
                <Flex justify="space-between" align="center">
                  <Heading size="md">{quiz.title}</Heading>
                  <Badge colorScheme={getDifficultyColor(quiz.difficulty)}>
                    {quiz.difficulty}
                  </Badge>
                </Flex>
              </Card.Header>
              <Card.Body>
                <Text mb={4}>{quiz.description}</Text>
                <HStack mb={2}>
                  <Tag.Root size="sm" colorScheme="blue">
                    <Tag.Label>{quiz.question_count} questions</Tag.Label>
                  </Tag.Root>
                  <Tag.Root size="sm" colorScheme="green">
                    <Tag.Label>
                      <Box as={FiClock} mr={1} />
                      {quiz.estimated_time_minutes} min
                    </Tag.Label>
                  </Tag.Root>
                  <Tag.Root size="sm" colorScheme="purple">
                    <Tag.Label>{quiz.topic}</Tag.Label>
                  </Tag.Root>
                </HStack>

                {quiz.last_attempt && (
                  <Box mt={4}>
                    <Text fontWeight="medium" mb={2}>Last Attempt:</Text>
                    <Text fontSize="sm" mb={1}>
                      {new Date(quiz.last_attempt.date).toLocaleDateString()}
                    </Text>
                    <Flex align="center" mb={1}>
                      <Text fontSize="sm" mr={2}>Score: {quiz.last_attempt.score}%</Text>
                      <Progress.Root
                        value={quiz.last_attempt.score}
                        size="sm"
                        colorPalette={getScoreColor(quiz.last_attempt.score)}
                        shape="full"
                        width="100px"
                      >
                        <Progress.Track>
                          <Progress.Range />
                        </Progress.Track>
                      </Progress.Root>
                    </Flex>
                  </Box>
                )}
              </Card.Body>
              <Card.Footer>
                <Button
                  colorScheme="blue"
                  size="sm"
                  width="full"
                  asChild
                >
                  <a href={`/quizzes/${quiz.id}`}>
                    {quiz.last_attempt ? 'Retake Quiz' : 'Start Quiz'}
                  </a>
                </Button>
              </Card.Footer>
            </Card.Root>
          ))}
        </SimpleGrid>
      )}
    </Container>
  );
};

export default QuizzesPage;
