import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Heading,
  Text,
  Container,
  Stack,
  Button,
  Progress,
  Card,
  Flex,
  Badge,
  Alert,
  Spinner,
  HStack,
  Tag,
  RadioGroup,
} from '@chakra-ui/react';
import { useColorModeValue } from '../components/ui/color-mode';
import { FiArrowLeft, FiClock, FiCheck, FiX } from 'react-icons/fi';
import { getQuiz, submitQuizAttempt, Quiz, QuizQuestion } from '../api/quizzes';

const QuizAttemptPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<number[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [quizStarted, setQuizStarted] = useState(false);
  const [quizResults, setQuizResults] = useState<any>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Use semantic tokens from theme
  const cardBg = "app.cardBg";
  const borderColor = "app.cardBorder";
  const textColor = "app.textColor";

  // Quiz-specific colors
  const optionBgLight = useColorModeValue('gray.50', 'gray.700');
  const optionBorderLight = useColorModeValue('gray.200', 'gray.600');
  const optionBgCorrect = useColorModeValue('green.50', 'green.900');
  const optionBorderCorrect = useColorModeValue('green.200', 'green.600');
  const optionBgIncorrect = useColorModeValue('red.50', 'red.900');
  const optionBorderIncorrect = useColorModeValue('red.200', 'red.600');

  useEffect(() => {
    const fetchQuiz = async () => {
      if (!id) return;

      try {
        setIsLoading(true);
        const data = await getQuiz(id);
        console.log('Fetched quiz:', data);
        setQuiz(data);
        // Initialize selected answers array with -1 (no selection)
        setSelectedAnswers(Array(data.questions.length).fill(-1));
      } catch (err) {
        console.error('Error fetching quiz:', err);
        setError('Failed to load quiz. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchQuiz();
  }, [id]);

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

  const handleAnswerSelect = (value: string | null) => {
    if (value === null) return;

    const newSelectedAnswers = [...selectedAnswers];
    newSelectedAnswers[currentQuestion] = parseInt(value);
    setSelectedAnswers(newSelectedAnswers);
  };

  const handleNext = () => {
    if (currentQuestion < (quiz?.questions.length || 0) - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      handleSubmitQuiz();
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const handleStartQuiz = () => {
    setQuizStarted(true);
  };

  const handleRestartQuiz = () => {
    setSelectedAnswers(Array(quiz?.questions.length || 0).fill(-1));
    setCurrentQuestion(0);
    setShowResults(false);
    setQuizResults(null);
  };

  const handleSubmitQuiz = async () => {
    if (!quiz || !id) return;

    try {
      setIsSubmitting(true);
      // Check if all questions have been answered
      const unansweredQuestions = selectedAnswers.filter(answer => answer === -1);
      if (unansweredQuestions.length > 0) {
        setError(`Please answer all questions before submitting. ${unansweredQuestions.length} questions are unanswered.`);
        return;
      }

      const results = await submitQuizAttempt(id, selectedAnswers);
      console.log('Quiz results:', results);
      setQuizResults(results);
      setShowResults(true);
      setError(null);
    } catch (err) {
      console.error('Error submitting quiz:', err);
      setError('Failed to submit quiz. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

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

  if (!quiz) {
    return (
      <Container maxW="container.lg" py={8}>
        <Alert.Root status="error" mb={6} borderRadius="md">
          <Alert.Indicator />
          <Alert.Title>Error!</Alert.Title>
          <Alert.Description>Quiz not found or failed to load.</Alert.Description>
        </Alert.Root>
        <Button onClick={() => navigate('/quizzes')}>
          <Box as={FiArrowLeft} mr={2} display="inline-block" /> Back to Quizzes
        </Button>
      </Container>
    );
  }

  if (!quizStarted) {
    return (
      <Container maxW="container.lg" py={8}>
        <Button mb={6} onClick={() => navigate('/quizzes')}>
          <Box as={FiArrowLeft} mr={2} display="inline-block" /> Back to Quizzes
        </Button>

        <Card.Root bg={cardBg} borderColor={borderColor} borderWidth="1px" borderRadius="lg" overflow="hidden">
          <Card.Header>
            <Flex justify="space-between" align="center">
              <Heading size="md" color="app.headingColor">{quiz.title}</Heading>
              <Badge colorScheme={getDifficultyColor(quiz.difficulty)}>
                {quiz.difficulty}
              </Badge>
            </Flex>
          </Card.Header>
          <Card.Body>
            <Text mb={4}>{quiz.description}</Text>
            <HStack mb={4}>
              <Tag.Root size="md" colorScheme="blue">
                <Tag.Label>
                  <Box as={FiClock} mr={1} display="inline-block" />
                  {quiz.estimated_time_minutes} minutes
                </Tag.Label>
              </Tag.Root>
              <Tag.Root size="md" colorScheme="green">
                <Tag.Label>{quiz.questions.length} questions</Tag.Label>
              </Tag.Root>
              <Tag.Root size="md" colorScheme="purple">
                <Tag.Label>{quiz.topic}</Tag.Label>
              </Tag.Root>
            </HStack>

            {error && (
              <Alert.Root status="error" mb={4} borderRadius="md">
                <Alert.Indicator />
                <Alert.Description>{error}</Alert.Description>
              </Alert.Root>
            )}

            <Text fontWeight="medium" mb={2}>Instructions:</Text>
            <Text mb={4}>
              This quiz contains {quiz.questions.length} multiple-choice questions.
              Read each question carefully and select the best answer.
              You can navigate between questions using the Previous and Next buttons.
            </Text>
          </Card.Body>
          <Card.Footer>
            <Button colorScheme="blue" width="full" onClick={handleStartQuiz}>
              Start Quiz
            </Button>
          </Card.Footer>
        </Card.Root>
      </Container>
    );
  }

  if (showResults && quizResults) {
    return (
      <Container maxW="container.lg" py={8}>
        <Button mb={6} onClick={() => navigate('/quizzes')}>
          <Box as={FiArrowLeft} mr={2} display="inline-block" /> Back to Quizzes
        </Button>

        <Card.Root bg={cardBg} borderColor={borderColor} borderWidth="1px" borderRadius="lg" overflow="hidden">
          <Card.Header>
            <Heading size="md" color="app.headingColor">Quiz Results: {quiz.title}</Heading>
          </Card.Header>
          <Card.Body>
            <Box textAlign="center" p={4}>
              <Heading size="xl" mb={2}>
                {quizResults.score}%
              </Heading>
              <Text fontSize="lg" mb={4}>
                You got {quizResults.correct_answers} out of {quizResults.total_questions} questions correct
              </Text>
              <Progress.Root
                value={quizResults.score}
                size="lg"
                colorPalette={getScoreColor(quizResults.score)}
                borderRadius="md"
                mb={6}
              >
                <Progress.Track>
                  <Progress.Range />
                </Progress.Track>
              </Progress.Root>
            </Box>

            <Stack direction="column" gap={4}>
              {quiz.questions.map((question: QuizQuestion, index: number) => (
                <Card.Root key={index} variant="outline">
                  <Card.Header pb={2}>
                    <Flex justify="space-between" align="center">
                      <Heading size="sm">Question {index + 1}</Heading>
                      {selectedAnswers[index] === question.correct_answer ? (
                        <Badge colorScheme="green">Correct</Badge>
                      ) : (
                        <Badge colorScheme="red">Incorrect</Badge>
                      )}
                    </Flex>
                  </Card.Header>
                  <Card.Body py={2}>
                    <Text mb={2}>{question.question}</Text>
                    <Stack direction="column" gap={2}>
                      {question.options.map((option, optIndex) => (
                        <Flex
                          key={optIndex}
                          p={2}
                          borderRadius="md"
                          bg={
                            optIndex === question.correct_answer
                              ? optionBgCorrect
                              : optIndex === selectedAnswers[index] && optIndex !== question.correct_answer
                              ? optionBgIncorrect
                              : optionBgLight
                          }
                          borderWidth="1px"
                          borderColor={
                            optIndex === question.correct_answer
                              ? optionBorderCorrect
                              : optIndex === selectedAnswers[index] && optIndex !== question.correct_answer
                              ? optionBorderIncorrect
                              : optionBorderLight
                          }
                        >
                          <Text>{option}</Text>
                          {optIndex === question.correct_answer && (
                            <Box ml="auto">
                              <FiCheck color="green" />
                            </Box>
                          )}
                          {optIndex === selectedAnswers[index] && optIndex !== question.correct_answer && (
                            <Box ml="auto">
                              <FiX color="red" />
                            </Box>
                          )}
                        </Flex>
                      ))}
                    </Stack>
                    <Text mt={2} fontSize="sm" color={textColor}>
                      {question.explanation}
                    </Text>
                  </Card.Body>
                </Card.Root>
              ))}
            </Stack>
          </Card.Body>
          <Card.Footer>
            <Button colorScheme="blue" width="full" onClick={handleRestartQuiz}>
              Retake Quiz
            </Button>
          </Card.Footer>
        </Card.Root>
      </Container>
    );
  }

  return (
    <Container maxW="container.lg" py={8}>
      <Button mb={6} onClick={() => navigate('/quizzes')}>
        <Box as={FiArrowLeft} mr={2} display="inline-block" /> Back to Quizzes
      </Button>

      <Card.Root bg={cardBg} borderColor={borderColor} borderWidth="1px" borderRadius="lg" overflow="hidden">
        <Card.Header>
          <Flex justify="space-between" align="center">
            <Heading size="md" color="app.headingColor">{quiz.title}</Heading>
            <Text>Question {currentQuestion + 1} of {quiz.questions.length}</Text>
          </Flex>
        </Card.Header>
        <Card.Body>
          {error && (
            <Alert.Root status="error" mb={4} borderRadius="md">
              <Alert.Indicator />
              <Alert.Description>{error}</Alert.Description>
            </Alert.Root>
          )}

          <Progress.Root
            value={(currentQuestion + 1) / quiz.questions.length * 100}
            size="sm"
            colorPalette="blue"
            borderRadius="md"
            mb={4}
          >
            <Progress.Track>
              <Progress.Range />
            </Progress.Track>
          </Progress.Root>

          <Box p={4} borderWidth="1px" borderColor={borderColor} borderRadius="md" mb={4}>
            <Text fontWeight="bold" mb={4}>{quiz.questions[currentQuestion].question}</Text>

            <RadioGroup.Root
              onValueChange={(details) => handleAnswerSelect(details.value)}
              value={selectedAnswers[currentQuestion].toString()}
            >
              <Stack direction="column" gap={3}>
                {quiz.questions[currentQuestion].options.map((option, index) => (
                  <RadioGroup.Item key={index} value={index.toString()}>
                    <RadioGroup.ItemHiddenInput />
                    <RadioGroup.ItemIndicator />
                    <RadioGroup.ItemText>{option}</RadioGroup.ItemText>
                  </RadioGroup.Item>
                ))}
              </Stack>
            </RadioGroup.Root>
          </Box>
        </Card.Body>
        <Card.Footer>
          <Flex justify="space-between" width="100%">
            <Button
              onClick={handlePrevious}
              disabled={currentQuestion === 0}
              variant="outline"
            >
              Previous
            </Button>

            {currentQuestion === quiz.questions.length - 1 ? (
              <Button
                onClick={handleSubmitQuiz}
                colorScheme="green"
                loading={isSubmitting}
                disabled={selectedAnswers[currentQuestion] === -1 || isSubmitting}
              >
                {isSubmitting ? "Submitting..." : "Submit Quiz"}
              </Button>
            ) : (
              <Button
                onClick={handleNext}
                colorScheme="blue"
                disabled={selectedAnswers[currentQuestion] === -1}
              >
                Next
              </Button>
            )}
          </Flex>
        </Card.Footer>
      </Card.Root>
    </Container>
  );
};

export default QuizAttemptPage;
