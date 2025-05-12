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
  Link,
  Input,
  InputGroup,
  Select,
  Portal,
  createListCollection,
} from '@chakra-ui/react';

import { ExternalLinkIcon } from '../components/ui/custom-icons';
import { LuSearch } from "react-icons/lu";

interface Resource {
  id: string;
  title: string;
  url: string;
  type: string;
  description: string;
  difficulty: string;
  estimated_time: string;
  topics: string[];
  source: string;
}

const ResourcesPage = () => {
  const [resources, setResources] = useState<Resource[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');

  // Use semantic tokens from theme
  const cardBg = "app.cardBg";
  const borderColor = "app.cardBorder";

  const resourceTypes = createListCollection({
    items: [
      { label: 'All Types', value: 'all' },
      { label: 'Articles', value: 'article' },
      { label: 'Videos', value: 'video' },
      { label: 'Courses', value: 'course' },
      { label: 'Books', value: 'book' },
      { label: 'Tutorials', value: 'tutorial' },
    ],
  });

  useEffect(() => {
    const fetchResources = async () => {
      try {
        // Replace with actual API call when backend is ready
        const response = await fetch('/api/v1/resources');

        if (!response.ok) {
          throw new Error('Failed to fetch resources');
        }

        const data = await response.json();
        setResources(data);
      } catch (err) {
        console.error('Error fetching resources:', err);
        setError('Failed to load resources. Please try again later.');

        // For development: mock data until backend is ready
        setResources([
          {
            id: '1',
            title: 'Python for Beginners',
            url: 'https://www.python.org/about/gettingstarted/',
            type: 'article',
            description: 'Official Python getting started guide',
            difficulty: 'beginner',
            estimated_time: '30 minutes',
            topics: ['Python', 'Programming Basics'],
            source: 'python.org'
          },
          {
            id: '2',
            title: 'Introduction to HTML and CSS',
            url: 'https://www.freecodecamp.org/learn/responsive-web-design/',
            type: 'course',
            description: 'Learn HTML and CSS fundamentals with interactive exercises',
            difficulty: 'beginner',
            estimated_time: '10 hours',
            topics: ['HTML', 'CSS', 'Web Development'],
            source: 'freecodecamp.org'
          },
          {
            id: '3',
            title: 'JavaScript Crash Course',
            url: 'https://www.youtube.com/watch?v=hdI2bqOjy3c',
            type: 'video',
            description: 'Quick introduction to JavaScript fundamentals',
            difficulty: 'beginner',
            estimated_time: '90 minutes',
            topics: ['JavaScript', 'Web Development'],
            source: 'YouTube'
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchResources();
  }, []);

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

  // Filter resources based on search query and type filter
  const filteredResources = resources.filter(resource => {
    const matchesSearch = resource.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         resource.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         resource.topics.some(topic => topic.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesType = filterType === 'all' || resource.type.toLowerCase() === filterType.toLowerCase();

    return matchesSearch && matchesType;
  });

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
          Learning Resources
        </Heading>
        <Text fontSize="lg" color="app.textColor">
          Curated educational materials to support your learning journey
        </Text>
      </Box>

      {error && (
        <Alert.Root status="error" mb={6} borderRadius="md">
          <Alert.Indicator />
          <Alert.Title>Error!</Alert.Title>
          <Alert.Description>{error}</Alert.Description>
        </Alert.Root>
      )}

      <Flex mb={6} gap={4} direction={{ base: 'column', md: 'row' }}>
        <InputGroup flex="1" startElement={<Box as={LuSearch} color="gray.500" />}>
          <Input
            placeholder="Search resources..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </InputGroup>
        <Select.Root
          collection={resourceTypes}
          value={[filterType]}
          onValueChange={(e) => setFilterType(e.value[0] || 'all')}
          width={{ base: 'full', md: '200px' }}
        >
          <Select.HiddenSelect />
          <Select.Control>
            <Select.Trigger>
              <Select.ValueText placeholder="Select type" />
            </Select.Trigger>
            <Select.IndicatorGroup>
              <Select.Indicator />
            </Select.IndicatorGroup>
          </Select.Control>
          <Portal>
            <Select.Positioner>
              <Select.Content>
                {resourceTypes.items.map((item) => (
                  <Select.Item item={item} key={item.value}>
                    {item.label}
                    <Select.ItemIndicator />
                  </Select.Item>
                ))}
              </Select.Content>
            </Select.Positioner>
          </Portal>
        </Select.Root>
      </Flex>

      {filteredResources.length === 0 ? (
        <Box textAlign="center" p={8} borderWidth="1px" borderRadius="lg">
          <Text mb={4}>No resources found matching your criteria.</Text>
          <Button colorScheme="blue" onClick={() => {setSearchQuery(''); setFilterType('all');}}>
            Clear Filters
          </Button>
        </Box>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2 }} gap={6}>
          {filteredResources.map((resource) => (
            <Card.Root key={resource.id} bg={cardBg} borderColor={borderColor} borderWidth="1px" borderRadius="lg" overflow="hidden">
              <Card.Header>
                <Flex justify="space-between" align="center">
                  <Heading size="md" color="app.headingColor">{resource.title}</Heading>
                  <Badge colorScheme={getResourceTypeColor(resource.type)}>
                    {resource.type}
                  </Badge>
                </Flex>
              </Card.Header>
              <Card.Body>
                <Text mb={4}>{resource.description}</Text>
                <HStack mb={2}>
                  <Tag.Root size="sm" colorScheme="blue">
                    {resource.difficulty}
                  </Tag.Root>
                  <Tag.Root size="sm" colorScheme="green">
                    {resource.estimated_time}
                  </Tag.Root>
                </HStack>
                <Box mt={4}>
                  <Text fontWeight="medium" mb={2}>Topics:</Text>
                  <Flex flexWrap="wrap" gap={2}>
                    {resource.topics.map((topic, index) => (
                      <Badge key={index} colorScheme="gray">
                        {topic}
                      </Badge>
                    ))}
                  </Flex>
                </Box>
              </Card.Body>
              <Card.Footer>
                <Link href={resource.url} _hover={{ textDecoration: 'none' }} width="full" target="_blank" rel="noopener noreferrer">
                  <Button
                    colorScheme="blue"
                    size="sm"
                    width="full"
                  >
                    View Resource <Box ml={4}><ExternalLinkIcon /></Box>
                  </Button>
                </Link>
              </Card.Footer>
            </Card.Root>
          ))}
        </SimpleGrid>
      )}
    </Container>
  );
};

export default ResourcesPage;
