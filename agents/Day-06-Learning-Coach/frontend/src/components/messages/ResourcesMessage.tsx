import { useState } from 'react';
import {
  Box,
  Heading,
  Text,
  Stack,
  HStack,
  Badge,
  Flex,
  Button,
  Alert
} from '@chakra-ui/react';
import { useColorModeValue } from '../ui/color-mode';
import { ExternalLinkIcon, TimeIcon, InfoIcon } from '../ui/custom-icons';
import { Divider } from '../ui/accordion';
import { Card, CardHeader, CardBody, CardFooter } from '../ui/card';
import { Tag } from '../ui/tag';
import { saveResourcesFromChat } from '../../api/resources';
import { FiSave } from 'react-icons/fi';

interface Resource {
  title: string;
  url: string;
  type: string;
  description: string;
  difficulty: string;
  estimated_time: string;
  topics: string[];
  source: string;
}

interface ResourcesData {
  resources: Resource[];
  query: string;
  total_count: number;
}

interface ResourcesMessageProps {
  data: ResourcesData;
}

const ResourcesMessage = ({ data }: ResourcesMessageProps) => {
  // State for saving resources
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<'success' | 'error' | null>(null);

  // Function to save resources
  const handleSaveResources = async () => {
    try {
      setIsSaving(true);
      await saveResourcesFromChat(data.resources);
      setSaveSuccess(true);
      setSaveMessage("Your resources have been saved successfully");
      setSaveStatus("success");

      // Auto-hide the message after 5 seconds
      setTimeout(() => {
        setSaveMessage(null);
      }, 5000);
    } catch (error) {
      console.error("Error saving resources:", error);
      setSaveMessage("There was an error saving your resources");
      setSaveStatus("error");

      // Auto-hide the message after 5 seconds
      setTimeout(() => {
        setSaveMessage(null);
      }, 5000);
    } finally {
      setIsSaving(false);
    }
  };

  // Color mode values
  const cardBg = useColorModeValue('white', 'gray.700');
  const headingColor = useColorModeValue('blue.600', 'blue.300');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  // Function to get color based on resource type
  const getResourceTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'video':
        return 'red';
      case 'article':
        return 'blue';
      case 'course':
        return 'green';
      case 'book':
        return 'purple';
      case 'tutorial':
        return 'orange';
      default:
        return 'gray';
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
      <Stack direction="column" align="stretch" gap={4}>
        <Stack gap={2}>
          <Flex justify="space-between" align="center">
            <Box>
              <Heading size="md" color={headingColor}>Learning Resources</Heading>
              <Text mt={2} color={textColor}>
                Found {data.total_count} resources for "{data.query}"
              </Text>
            </Box>

            <Button
              colorScheme="green"
              size="sm"
              onClick={handleSaveResources}
              disabled={saveSuccess || isSaving}
            >
              <Box as={FiSave} mr={2} />
              {isSaving ? "Saving..." : saveSuccess ? "Saved" : "Save Resources"}
            </Button>
          </Flex>

          {saveMessage && (
            <Alert.Root status={saveStatus || "info"}>
              <Alert.Indicator />
              <Alert.Content>
                <Alert.Description>{saveMessage}</Alert.Description>
              </Alert.Content>
            </Alert.Root>
          )}
        </Stack>

        <Divider />

        <Box display="grid" gridTemplateColumns={{ base: "1fr", md: "1fr 1fr" }} gap={4}>
          {data.resources.map((resource, index) => (
            <Card key={index} variant="outline">
              <CardHeader pb={2}>
                <Flex justify="space-between" align="flex-start">
                  <Heading size="sm">{resource.title}</Heading>
                  <Badge
                    colorScheme={getResourceTypeColor(resource.type)}
                    fontSize="0.7em"
                  >
                    {resource.type}
                  </Badge>
                </Flex>
              </CardHeader>

              <CardBody py={2}>
                <Text fontSize="sm">{resource.description.substring(0, 100)}...</Text>

                <HStack mt={2} gap={2} flexWrap="wrap">
                  <Tag size="sm" colorScheme={getDifficultyColor(resource.difficulty)}>
                    {resource.difficulty}
                  </Tag>
                  <Tag size="sm" variant="outline">
                    <Box as={TimeIcon} boxSize="0.8em" mr={1} />
                    <Text>{resource.estimated_time}</Text>
                  </Tag>
                  <Tag size="sm" variant="subtle">
                    <Box as={InfoIcon} boxSize="0.8em" mr={1} />
                    <Text>{resource.source}</Text>
                  </Tag>
                </HStack>
              </CardBody>

              <CardFooter pt={2}>
                <a
                  href={resource.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ width: '100%', display: 'block' }}
                >
                  <Button
                    size="sm"
                    colorScheme="blue"
                    width="100%"
                  >
                    View Resource
                    <Box as={ExternalLinkIcon} ml={2} />
                  </Button>
                </a>
              </CardFooter>
            </Card>
          ))}
        </Box>
      </Stack>
    </Box>
  );
};

export default ResourcesMessage;
