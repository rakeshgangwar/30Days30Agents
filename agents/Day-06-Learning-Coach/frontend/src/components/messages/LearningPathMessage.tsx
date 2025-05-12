import { useState } from 'react';
import {
  Box,
  Heading,
  Text,
  Stack,
  HStack,
  Badge,
  List,
  ListItem,
  Button,
  Flex,
  Tag,
  Tooltip
} from '@chakra-ui/react';
import { useColorModeValue } from '../ui/color-mode';
import { CheckCircleIcon, TimeIcon, ExternalLinkIcon } from '../ui/custom-icons';
import { Accordion, AccordionItem, AccordionButton, AccordionPanel, AccordionIcon, Divider } from '../ui/accordion';

interface LearningPathTopic {
  title: string;
  description: string;
  estimated_hours: number;
  prerequisites: string[];
  resources: Array<{
    title: string;
    url: string;
    type: string;
    description: string;
  }>;
}

interface LearningPath {
  title: string;
  description: string;
  topics: LearningPathTopic[];
  difficulty: string;
  estimated_total_hours: number;
}

interface LearningPathMessageProps {
  data: LearningPath;
}

const LearningPathMessage = ({ data }: LearningPathMessageProps) => {
  const [expanded, setExpanded] = useState(false);

  // Color mode values
  const cardBg = useColorModeValue('white', 'gray.700');
  const headingColor = useColorModeValue('blue.600', 'blue.300');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

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

  return (
    <Box
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      overflow="hidden"
      p={4}
      bg={cardBg}
      boxShadow="md"
      w="100%"
    >
      <Stack direction="column" gap={4} align="stretch">
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
          <Tooltip label="Estimated total time to complete">
            <Tag size="md" variant="subtle" colorScheme="blue">
              <Box as={TimeIcon} mr={1} />
              <Text>{data.estimated_total_hours} hours total</Text>
            </Tag>
          </Tooltip>
          <Tooltip label="Number of topics">
            <Tag size="md" variant="subtle" colorScheme="green">
              <Text>{data.topics.length} topics</Text>
            </Tag>
          </Tooltip>
        </HStack>

        <Divider />

        <Accordion>
          {data.topics.map((topic, index) => (
            <AccordionItem
              key={index}
              title={
                <Flex justify="space-between" align="center" width="100%">
                  <Text fontWeight="bold">{topic.title}</Text>
                  <HStack gap={2}>
                    <Tag size="sm" colorScheme="blue" variant="outline">
                      <Box as={TimeIcon} boxSize="0.8em" mr={1} />
                      <Text>{topic.estimated_hours}h</Text>
                    </Tag>
                  </HStack>
                </Flex>
              }
              isOpen={index === 0}
            >
              <Stack direction="column" gap={3} align="stretch">
                <Text>{topic.description}</Text>

                {topic.prerequisites.length > 0 && (
                  <Box>
                    <Text fontWeight="medium">Prerequisites:</Text>
                    <List ml={4}>
                      {topic.prerequisites.map((prereq, i) => (
                        <ListItem key={i} display="flex" alignItems="center" mt={1}>
                          <Box as={CheckCircleIcon} color="green.500" mr={2} />
                          {prereq}
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}

                {topic.resources.length > 0 && (
                  <Box>
                    <Text fontWeight="medium">Resources:</Text>
                    <List ml={4}>
                      {topic.resources.map((resource, i) => (
                        <ListItem key={i} mt={1}>
                          <Flex align="center">
                            <Box as={ExternalLinkIcon} color="blue.500" mr={2} />
                            <Text>{resource.title}</Text>
                            <Badge ml={2} colorScheme="gray" fontSize="0.7em">
                              {resource.type}
                            </Badge>
                          </Flex>
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </Stack>
            </AccordionItem>
          ))}
        </Accordion>

        <Button
          colorScheme="blue"
          size="sm"
          alignSelf="center"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "Collapse" : "View Full Learning Path"}
        </Button>
      </Stack>
    </Box>
  );
};

export default LearningPathMessage;
