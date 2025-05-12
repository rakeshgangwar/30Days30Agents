import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  Box,
  Heading,
  Text,
  Container,
  Button,
  Flex,
  Spinner,
  Alert,
  Stack,
  Badge,
  HStack,
  Icon,
  Accordion,
  List,
  Card,
  Tag,
  Progress,
  Checkbox,
} from "@chakra-ui/react";

import {
  FiClock,
  FiArrowLeft,
  FiExternalLink,
  FiCheckCircle,
} from "react-icons/fi";
import { getLearningPath, updateLearningPath } from "../api/learning-paths";
import { LearningPath } from "../api/learning-paths";

const LearningPathViewPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [learningPath, setLearningPath] = useState<LearningPath | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Use semantic tokens from theme
  const cardBg = "app.cardBg";
  const borderColor = "app.cardBorder";
  const headingColor = "app.headingColor";
  const textColor = "app.textColor";

  useEffect(() => {
    const fetchLearningPath = async () => {
      if (!id) return;

      try {
        setIsLoading(true);
        const data = await getLearningPath(parseInt(id));
        console.log("Learning path data:", data);
        console.log("Resources:", data.resources);
        setLearningPath(data);
      } catch (err) {
        console.error("Error fetching learning path:", err);
        setError("Failed to load learning path. Please try again later.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchLearningPath();
  }, [id]);

  const handleTopicCompletion = async (
    topicIndex: number,
    isCompleted: boolean
  ) => {
    console.log(
      `handleTopicCompletion called with topicIndex: ${topicIndex}, isCompleted: ${isCompleted}`
    );

    if (!learningPath || !id) {
      console.error("No learning path or ID available");
      return;
    }

    try {
      // Get the topic being marked as completed/uncompleted
      const topic = learningPath.topics[topicIndex];
      if (!topic) {
        console.error(`No topic found at index ${topicIndex}`);
        return;
      }

      console.log(
        `Handling completion for topic: ${topic.name} (order: ${topic.order})`
      );

      // Create a copy of the current progress
      const updatedProgress = { ...learningPath.progress };
      console.log("Current progress:", updatedProgress);

      // Initialize completed_topic_ids array if it doesn't exist
      if (!updatedProgress.completed_topic_ids) {
        console.log("Initializing completed_topic_ids array");
        updatedProgress.completed_topic_ids = [] as number[];
      }

      // Ensure completed_topic_ids is treated as a number array
      const completedTopicIds = updatedProgress.completed_topic_ids as number[];
      console.log("Current completed topic IDs:", completedTopicIds);

      // Update completed_topic_ids array
      if (isCompleted) {
        // Add topic to completed topics if not already there
        if (!completedTopicIds.includes(topic.order)) {
          console.log(`Adding topic ${topic.order} to completed topics`);
          completedTopicIds.push(topic.order);
        } else {
          console.log(`Topic ${topic.order} already in completed topics`);
        }
      } else {
        // Remove topic from completed topics
        const index = completedTopicIds.indexOf(topic.order);
        if (index !== -1) {
          console.log(`Removing topic ${topic.order} from completed topics`);
          completedTopicIds.splice(index, 1);
        } else {
          console.log(`Topic ${topic.order} not found in completed topics`);
        }
      }

      // Update the array in the progress object
      updatedProgress.completed_topic_ids = completedTopicIds;

      // Update completed_topics count based on the array length
      updatedProgress.completed_topics = completedTopicIds.length;

      console.log("Updated progress:", updatedProgress);

      // Create a properly typed progress object for the API
      const progressUpdate = {
        completed_topics: updatedProgress.completed_topics,
        total_topics: updatedProgress.total_topics,
        completed_topic_ids: completedTopicIds,
      };

      console.log("Sending progress update to API:", progressUpdate);

      // Update the learning path with the new progress
      const updatedLearningPath = await updateLearningPath(parseInt(id), {
        progress: progressUpdate,
      });

      console.log(
        "Received updated learning path from API:",
        updatedLearningPath
      );
      setLearningPath(updatedLearningPath);
    } catch (err) {
      console.error("Error updating topic completion:", err);
      setError("Failed to update progress. Please try again.");
    }
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

  if (error || !learningPath) {
    return (
      <Container maxW="container.lg" py={8}>
        <Button mb={6} onClick={() => navigate("/learning-paths")}>
          <Box as={FiArrowLeft} mr={2} display="inline-block" /> Back to Learning Paths
        </Button>

        <Alert.Root status="error" mb={6} borderRadius="md">
          <Alert.Indicator />
          <Alert.Title>Error!</Alert.Title>
          <Alert.Description>
            {error || "Learning path not found"}
          </Alert.Description>
        </Alert.Root>
      </Container>
    );
  }

  const progressPercentage = Math.round(
    (learningPath.progress.completed_topics /
      learningPath.progress.total_topics) *
      100
  );

  return (
    <Container maxW="container.lg" py={8}>
      <Button mb={6} onClick={() => navigate("/learning-paths")}>
        <Box as={FiArrowLeft} mr={2} display="inline-block" /> Back to Learning Paths
      </Button>

      <Card.Root
        bg={cardBg}
        borderColor={borderColor}
        borderWidth="1px"
        borderRadius="lg"
        overflow="hidden"
        mb={6}
      >
        <Card.Header>
          <Heading as="h1" size="xl" color="app.pageTitleColor">
            {learningPath.title}
          </Heading>
          <Text mt={2} color={textColor}>
            {learningPath.description}
          </Text>
        </Card.Header>

        <Card.Body>
          <Stack gap={6}>
            <Box>
              <Flex justify="space-between" align="center" mb={2}>
                <Text fontWeight="bold">Overall Progress</Text>
                <Text>{progressPercentage}% Complete</Text>
              </Flex>
              <Progress.Root value={progressPercentage} max={100}>
                <Progress.Track>
                  <Progress.Range bg="green.500" borderRadius="md" />
                </Progress.Track>
              </Progress.Root>
            </Box>

            <HStack>
              <Tag.Root size="md" colorScheme="blue">
                <Tag.Label>
                  <Icon as={FiClock} mr={1} />
                  {learningPath.topics.length} topics
                </Tag.Label>
              </Tag.Root>
              <Tag.Root size="md" colorScheme="green">
                <Tag.Label>
                  <Icon as={FiCheckCircle} mr={1} />
                  {learningPath.progress.completed_topics} completed
                </Tag.Label>
              </Tag.Root>
            </HStack>
          </Stack>
        </Card.Body>
      </Card.Root>

      <Box mb={8}>
        <Heading as="h2" size="lg" mb={4} color="app.headingColor">
          Topics
        </Heading>
        <Accordion.Root defaultValue={["0"]}>
          {learningPath.topics.map((topic, index) => (
            <Accordion.Item key={index} value={index.toString()}>
              <Accordion.ItemTrigger>
                <Flex
                  justify="space-between"
                  align="center"
                  width="100%"
                  py={2}
                >
                  <HStack>
                    <Badge colorScheme="blue" mr={2}>
                      {topic.order}
                    </Badge>
                    <Text fontWeight="bold">{topic.name}</Text>
                  </HStack>
                  <Checkbox.Root
                    checked={
                      learningPath.progress.completed_topic_ids
                        ? (
                            learningPath.progress
                              .completed_topic_ids as number[]
                          ).includes(topic.order)
                        : index < learningPath.progress.completed_topics
                    }
                    onCheckedChange={(details) => {
                      console.log("Checkbox onCheckedChange:", details);
                      // The details object has a checked property that can be a string or boolean
                      handleTopicCompletion(index, details.checked === true);
                    }}
                    onClick={(e: React.MouseEvent) => {
                      console.log("Checkbox onClick event:", e);
                      e.stopPropagation();
                    }}
                    colorPalette="green"
                  >
                    <Checkbox.HiddenInput />
                    <Checkbox.Control>
                      <Checkbox.Indicator />
                    </Checkbox.Control>
                  </Checkbox.Root>
                </Flex>
              </Accordion.ItemTrigger>
              <Accordion.ItemContent px={4} pb={4}>
                <Stack gap={4}>
                  {/* If we have resources for this topic, display them */}
                  {learningPath.resources &&
                    learningPath.resources.length > 0 && (
                      <Box>
                        <Text fontWeight="medium" mb={2}>
                          Resources:
                        </Text>
                        <List.Root gap={2}>
                          {(() => {
                            console.log(
                              `Filtering resources for topic ${topic.name} (order: ${topic.order})`
                            );

                            // First try to find resources specifically for this topic
                            let filteredResources =
                              learningPath.resources.filter((resource) => {
                                const matches =
                                  resource.topic_order === topic.order ||
                                  (resource.topic &&
                                    resource.topic.order === topic.order) ||
                                  resource.topic_id === topic.order ||
                                  resource.topic_id ===
                                    topic.order.toString() ||
                                  resource.topic_name === topic.name;
                                console.log(
                                  `Resource ${
                                    resource.name || resource.title
                                  }: matches=${matches}`,
                                  resource
                                );
                                return matches;
                              });

                            console.log(
                              `Found ${filteredResources.length} resources for topic ${topic.name}`
                            );

                            // If we don't have any resources for this topic, check if we have any resources
                            // that might be associated with this topic in a different way
                            if (filteredResources.length === 0) {
                              // Try to match by topic name in the topics array
                              filteredResources = learningPath.resources.filter(
                                (resource) => {
                                  if (Array.isArray(resource.topics)) {
                                    return resource.topics.some(
                                      (t) =>
                                        (typeof t === "string" &&
                                          t.toLowerCase() ===
                                            topic.name.toLowerCase()) ||
                                        (typeof t === "object" &&
                                          t.name &&
                                          t.name.toLowerCase() ===
                                            topic.name.toLowerCase())
                                    );
                                  }
                                  return false;
                                }
                              );
                              console.log(
                                `Found ${filteredResources.length} resources by matching topic name in topics array`
                              );
                            }

                            // If this is the first topic and we still don't have any resources specifically for it,
                            // show resources that don't have a topic association
                            if (
                              filteredResources.length === 0 &&
                              topic.order === 1
                            ) {
                              filteredResources = learningPath.resources.filter(
                                (resource) => {
                                  const hasNoTopicAssociation =
                                    !resource.topic_order &&
                                    !resource.topic &&
                                    !resource.topic_id &&
                                    !resource.topic_name;
                                  return hasNoTopicAssociation;
                                }
                              );
                              console.log(
                                `Found ${filteredResources.length} resources with no topic association`
                              );
                            }

                            return filteredResources;
                          })().map((resource, resourceIndex) => (
                            <List.Item key={resourceIndex}>
                              <Card.Root variant="outline" size="sm">
                                <Card.Body>
                                  <Flex justify="space-between" align="center">
                                    <Box>
                                      <Text fontWeight="medium">
                                        {resource.name || resource.title}
                                      </Text>
                                      <Text fontSize="sm">
                                        {resource.description}
                                      </Text>
                                    </Box>
                                    <Button size="sm" variant="outline" asChild>
                                      <a
                                        href={resource.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                      >
                                        Open{" "}
                                        <Box
                                          as={FiExternalLink}
                                          ml={1}
                                          display="inline-block"
                                        />
                                      </a>
                                    </Button>
                                  </Flex>
                                </Card.Body>
                              </Card.Root>
                            </List.Item>
                          ))}
                        </List.Root>
                      </Box>
                    )}
                </Stack>
              </Accordion.ItemContent>
            </Accordion.Item>
          ))}
        </Accordion.Root>
      </Box>
    </Container>
  );
};

export default LearningPathViewPage;
