import { useState } from 'react';
import {
  Box,
  Heading,
  Text,
  Stack,
  HStack,
  Badge,
  Button,
  Flex
} from '@chakra-ui/react';
import { useColorModeValue } from '../ui/color-mode';
import { CheckIcon, CloseIcon, TimeIcon, RepeatIcon } from '../ui/custom-icons';
import { Divider } from '../ui/accordion';
import { Card, CardHeader, CardBody, CardFooter } from '../ui/card';
import { Radio, RadioGroup } from '../ui/radio';
import { Progress } from '../ui/progress';
import { Tag } from '../ui/tag';

interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
}

interface QuizData {
  title: string;
  description: string;
  topic: string;
  difficulty: string;
  questions: QuizQuestion[];
  estimated_time_minutes: number;
}

interface QuizMessageProps {
  data: QuizData;
}

const QuizMessage = ({ data }: QuizMessageProps) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<number[]>(Array(data.questions.length).fill(-1));
  const [showResults, setShowResults] = useState(false);
  const [quizStarted, setQuizStarted] = useState(false);

  // Color mode values
  const cardBg = useColorModeValue('white', 'gray.700');
  const headingColor = useColorModeValue('blue.600', 'blue.300');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const optionBgLight = useColorModeValue('gray.50', 'gray.600');
  const optionBgCorrect = useColorModeValue('green.100', 'green.800');
  const optionBgIncorrect = useColorModeValue('red.100', 'red.800');
  const optionBorderLight = useColorModeValue('gray.200', 'gray.500');
  const optionBorderCorrect = useColorModeValue('green.300', 'green.600');
  const optionBorderIncorrect = useColorModeValue('red.300', 'red.600');

  // Function to get color based on difficulty
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'beginner':
        return 'green';
      case 'intermediate':
        return 'blue';
      case 'advanced':
        return 'purple';
      default:
        return 'gray';
    }
  };

  const handleAnswerSelect = (value: string) => {
    const newSelectedAnswers = [...selectedAnswers];
    newSelectedAnswers[currentQuestion] = parseInt(value);
    setSelectedAnswers(newSelectedAnswers);
  };

  const handleNext = () => {
    if (currentQuestion < data.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      setShowResults(true);
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
    setSelectedAnswers(Array(data.questions.length).fill(-1));
    setCurrentQuestion(0);
    setShowResults(false);
  };

  const calculateScore = () => {
    let correctAnswers = 0;
    selectedAnswers.forEach((selected, index) => {
      if (selected === data.questions[index].correct_answer) {
        correctAnswers++;
      }
    });
    return {
      score: correctAnswers,
      total: data.questions.length,
      percentage: Math.round((correctAnswers / data.questions.length) * 100)
    };
  };

  const score = calculateScore();

  if (!quizStarted) {
    return (
      <Box
        borderWidth="1px" borderColor={borderColor}
        borderRadius="lg"
        overflow="hidden"
        p={4}
        bg={cardBg}
        boxShadow="md"
        w="100%"
      >
        <Stack direction="column" align="stretch" gap={4}>
          <Box>
            <Flex justify="space-between" align="center">
              <Heading size="md" color={headingColor}>{data.title}</Heading>
              <Badge
                colorScheme={getDifficultyColor(data.difficulty)}
                fontSize="0.8em"
                p={1}
                borderRadius="md"
              >
                {data.difficulty}
              </Badge>
            </Flex>
            <Text mt={2} color={textColor}>{data.description}</Text>
          </Box>

          <HStack>
            <Tag size="md" variant="subtle" colorScheme="blue">
              <Box as={TimeIcon} mr={1} />
              <Text>{data.estimated_time_minutes} minutes</Text>
            </Tag>
            <Tag size="md" variant="subtle" colorScheme="green">
              <Text>{data.questions.length} questions</Text>
            </Tag>
          </HStack>

          <Divider />

          <Button
            colorScheme="blue"
            onClick={handleStartQuiz}
            alignSelf="center"
          >
            Start Quiz
          </Button>
        </Stack>
      </Box>
    );
  }

  if (showResults) {
    return (
      <Box
        borderWidth="1px" borderColor={borderColor}
        borderRadius="lg"
        overflow="hidden"
        p={4}
        bg={cardBg}
        boxShadow="md"
        w="100%"
      >
        <Stack direction="column" align="stretch" gap={4}>
          <Heading size="md" color={headingColor}>Quiz Results</Heading>

          <Box textAlign="center" p={4}>
            <Heading size="xl" mb={2}>
              {score.percentage}%
            </Heading>
            <Text fontSize="lg">
              You got {score.score} out of {score.total} questions correct
            </Text>
            <Progress
              value={score.percentage}
              colorScheme={score.percentage >= 70 ? "green" : score.percentage >= 40 ? "yellow" : "red"}
              size="lg"
              mt={4}
              borderRadius="md"
            />
          </Box>

          <Divider />

          <Stack direction="column" align="stretch" gap={4}>
            {data.questions.map((question, index) => (
              <Card key={index} variant="outline">
                <CardHeader pb={2}>
                  <Flex justify="space-between" align="center">
                    <Heading size="sm">Question {index + 1}</Heading>
                    {selectedAnswers[index] === question.correct_answer ? (
                      <Badge colorScheme="green">Correct</Badge>
                    ) : (
                      <Badge colorScheme="red">Incorrect</Badge>
                    )}
                  </Flex>
                </CardHeader>
                <CardBody py={2}>
                  <Text mb={2}>{question.question}</Text>
                  <Stack direction="column" align="stretch">
                    {question.options.map((option, optIndex) => (
                      <Flex
                        key={optIndex}
                        p={2}
                        borderRadius="md"
                        bg={
                          optIndex === question.correct_answer
                            ? {optionBgCorrect}
                            : optIndex === selectedAnswers[index] && optIndex !== question.correct_answer
                            ? {optionBgIncorrect}
                            : {optionBgLight}
                        }
                        borderWidth="1px" borderColor={borderColor}
                        borderColor={
                          optIndex === question.correct_answer
                            ? {optionBorderCorrect}
                            : optIndex === selectedAnswers[index] && optIndex !== question.correct_answer
                            ? {optionBorderIncorrect}
                            : {optionBorderLight}
                        }
                      >
                        <Text>{option}</Text>
                        {optIndex === question.correct_answer && (
                          <Box ml="auto">
                            <CheckIcon style={{ color: "green" }} />
                          </Box>
                        )}
                        {optIndex === selectedAnswers[index] && optIndex !== question.correct_answer && (
                          <Box ml="auto">
                            <CloseIcon style={{ color: "red" }} />
                          </Box>
                        )}
                      </Flex>
                    ))}
                  </Stack>
                  <Text mt={2} fontSize="sm" color={textColor}>
                    {question.explanation}
                  </Text>
                </CardBody>
              </Card>
            ))}
          </Stack>

          <Button

            colorScheme="blue"
            onClick={handleRestartQuiz}
            alignSelf="center"
          >
            <Box as={RepeatIcon} mr={2} /> Restart Quiz
          </Button>
        </Stack>
      </Box>
    );
  }

  return (
    <Box
      borderWidth="1px" borderColor={borderColor}
      borderRadius="lg"
      overflow="hidden"
      p={4}
      bg={cardBg}
      boxShadow="md"
      w="100%"
    >
      <Stack direction="column" align="stretch" gap={4}>
        <Flex justify="space-between" align="center">
          <Heading size="md" color={headingColor}>{data.title}</Heading>
          <Text>Question {currentQuestion + 1} of {data.questions.length}</Text>
        </Flex>

        <Progress
          value={(currentQuestion + 1) / data.questions.length * 100}
          size="sm"
          colorScheme="blue"
          borderRadius="md"
        />

        <Box p={4} borderWidth="1px" borderColor={borderColor} borderRadius="md">
          <Text fontWeight="bold" mb={4}>{data.questions[currentQuestion].question}</Text>

          <RadioGroup
            onChange={handleAnswerSelect}
            value={selectedAnswers[currentQuestion].toString()}
          >
            <Stack direction="column" gap={3}>
              {data.questions[currentQuestion].options.map((option, index) => (
                <Radio key={index} value={index.toString()}>
                  {option}
                </Radio>
              ))}
            </Stack>
          </RadioGroup>
        </Box>

        <HStack justify="space-between">
          <Button
            onClick={handlePrevious}
            disabled={currentQuestion === 0}
            variant="outline"
          >
            Previous
          </Button>
          <Button
            onClick={handleNext}
            colorScheme="blue"
            disabled={selectedAnswers[currentQuestion] === -1}
          >
            {currentQuestion === data.questions.length - 1 ? "Finish" : "Next"}
          </Button>
        </HStack>
      </Stack>
    </Box>
  );
};

export default QuizMessage;
