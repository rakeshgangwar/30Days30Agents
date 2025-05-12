import { useState } from 'react';
import {
  Box,
  Heading,
  Text,
  Stack,
  HStack,
  Badge,
  Button,
  Flex,
  List,
  ListItem,
  Tag,
  Tooltip,
  Alert
} from '@chakra-ui/react';
import { useColorModeValue } from '../ui/color-mode';
import { CheckCircleIcon, TimeIcon, ExternalLinkIcon } from '../ui/custom-icons';
import { Accordion, AccordionItem, Divider } from '../ui/accordion';
import { saveLearningPathFromChat } from '../../api/learning-paths';
import { FiSave } from 'react-icons/fi';

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
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false); // Initialize to false
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<'success' | 'error' | null>(null);

  // Color mode values
  const cardBg = useColorModeValue('white', 'gray.700');
  const headingColor = useColorModeValue('blue.600', 'blue.300');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  // Function to save the learning path
  const handleSaveLearningPath = async () => {
    try {
      setIsSaving(true);
      await saveLearningPathFromChat(data);
      setSaveSuccess(true);
      setSaveMessage("Your learning path has been saved successfully");
      setSaveStatus("success");

      // Auto-hide the message after 5 seconds
      setTimeout(() => {
        setSaveMessage(null);
      }, 5000);
      
      // Reset saveSuccess after 5 seconds so button becomes active again
      setTimeout(() => {
        setSaveSuccess(false);
      }, 5000);
    } catch (error) {
      console.error("Error saving learning path:", error);
      setSaveMessage("There was an error saving your learning path");
      setSaveStatus("error");

      // Auto-hide the message after 5 seconds
      setTimeout(() => {
        setSaveMessage(null);
      }, 5000);
    } finally {
      setIsSaving(false);
    }
  };

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
        <Stack gap={2}>
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

          {saveMessage && (
            <Alert.Root status={saveStatus || "info"}>
              <Alert.Content>
                <Alert.Description>{saveMessage}</Alert.Description>
              </Alert.Content>
            </Alert.Root>
          )}
        </Stack>

        <HStack>
          <Tooltip.Root>
            <Tooltip.Trigger>
              <Tag.Root size="md" variant="subtle" colorPalette="blue">
                <Tag.StartElement>
                  <Box as={TimeIcon} mr={1} />
                </Tag.StartElement>
                <Tag.Label>{data.estimated_total_hours} hours total</Tag.Label>
              </Tag.Root>
            </Tooltip.Trigger>
            <Tooltip.Positioner>
              <Tooltip.Content>
                Estimated total time to complete
              </Tooltip.Content>
            </Tooltip.Positioner>
          </Tooltip.Root>
          <Tooltip.Root>
            <Tooltip.Trigger>
              <Tag.Root size="md" variant="subtle" colorPalette="green">
                <Tag.Label>{data.topics.length} topics</Tag.Label>
              </Tag.Root>
            </Tooltip.Trigger>
            <Tooltip.Positioner>
              <Tooltip.Content>
                Number of topics
              </Tooltip.Content>
            </Tooltip.Positioner>
          </Tooltip.Root>
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
                    <Tag.Root size="sm" colorPalette="blue" variant="outline">
                      <Tag.StartElement>
                        <Box as={TimeIcon} boxSize="0.8em" mr={1} />
                      </Tag.StartElement>
                      <Tag.Label>{topic.estimated_hours}h</Tag.Label>
                    </Tag.Root>
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
                    <List.Root ml={4}>
                      {topic.prerequisites.map((prereq, i) => (
                        <List.Item key={i} display="flex" alignItems="center" mt={1}>
                          <Box as={CheckCircleIcon} color="green.500" mr={2} />
                          {prereq}
                        </List.Item>
                      ))}
                    </List.Root>
                  </Box>
                )}

                {topic.resources.length > 0 && (
                  <Box>
                    <Text fontWeight="medium">Resources:</Text>
                    <List.Root ml={4}>
                      {topic.resources.map((resource, i) => (
                        <List.Item key={i} mt={1}>
                          <Flex align="center">
                            <Box as={ExternalLinkIcon} color="blue.500" mr={2} />
                            <Text>{resource.title}</Text>
                            <Badge ml={2} colorScheme="gray" fontSize="0.7em">
                              {resource.type}
                            </Badge>
                          </Flex>
                        </List.Item>
                      ))}
                    </List.Root>
                  </Box>
                )}
              </Stack>
            </AccordionItem>
          ))}
        </Accordion>

        <Flex gap={4} alignSelf="center">
          <Button
            colorScheme="blue"
            size="sm"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? "Collapse" : "View Full Learning Path"}
          </Button>

          <Button
            colorScheme="green"
            size="sm"
            onClick={handleSaveLearningPath}
            disabled={isSaving}
          >
            <Box as={FiSave} mr={2} />
            {isSaving ? "Saving..." : saveSuccess ? "Saved" : "Save Learning Path"}
          </Button>
        </Flex>
      </Stack>
    </Box>
  );
};

export default LearningPathMessage;
