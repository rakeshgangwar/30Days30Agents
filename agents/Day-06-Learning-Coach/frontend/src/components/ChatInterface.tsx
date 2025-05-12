import { useState, useRef, useEffect } from 'react';
import {
  Box,
  Stack,
  HStack,
  Input,
  Button,
  Text,
  Flex
} from '@chakra-ui/react';
import { useColorModeValue } from './ui/color-mode';
import { ArrowUpIcon } from './ui/custom-icons';
import { chatWithAgent } from '../api/agent';
import {
  TextMessage,
  LearningPathMessage,
  ResourcesMessage,
  QuizMessage
} from './messages';

// Define message types
type MessageType = 'text' | 'learning_path' | 'resources' | 'quiz';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  type?: MessageType;
  data?: any;
}

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const bgColor = useColorModeValue('gray.50', 'gray.800');
  const userBubbleColor = useColorModeValue('blue.100', 'blue.600');
  const agentBubbleColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.800', 'white');
  const mutedTextColor = useColorModeValue('gray.500', 'gray.400');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Function to detect message type and extract structured data
  const processAgentResponse = (responseText: string): { type: MessageType; text: string; data?: any } => {
    // Default to text message
    let type: MessageType = 'text';
    let data = null;
    let text = responseText;

    try {
      // Check for learning path
      if (responseText.includes('"title"') &&
          responseText.includes('"topics"') &&
          responseText.includes('"difficulty"')) {

        // Try to extract JSON data
        const jsonMatch = responseText.match(/```json\n([\s\S]*?)\n```/);
        if (jsonMatch && jsonMatch[1]) {
          const jsonData = JSON.parse(jsonMatch[1]);
          if (jsonData.topics && Array.isArray(jsonData.topics)) {
            type = 'learning_path';
            data = jsonData;
            // Remove the JSON from the content
            text = responseText.replace(/```json\n[\s\S]*?\n```/, '');
          }
        } else if (responseText.includes('"estimated_total_hours"')) {
          // Try to find JSON without markdown code blocks
          const startIndex = responseText.indexOf('{');
          const endIndex = responseText.lastIndexOf('}') + 1;
          if (startIndex !== -1 && endIndex !== -1) {
            try {
              const jsonData = JSON.parse(responseText.substring(startIndex, endIndex));
              if (jsonData.topics && Array.isArray(jsonData.topics)) {
                type = 'learning_path';
                data = jsonData;
                // Remove the JSON from the content
                text = responseText.replace(responseText.substring(startIndex, endIndex), '');
              }
            } catch (e) {
              console.log('Failed to parse potential learning path JSON');
            }
          }
        }
      }

      // Check for resources
      else if (responseText.includes('"resources"') &&
               responseText.includes('"url"') &&
               responseText.includes('"type"')) {

        // Try to extract JSON data
        const jsonMatch = responseText.match(/```json\n([\s\S]*?)\n```/);
        if (jsonMatch && jsonMatch[1]) {
          const jsonData = JSON.parse(jsonMatch[1]);
          if (jsonData.resources && Array.isArray(jsonData.resources)) {
            type = 'resources';
            data = jsonData;
            // Remove the JSON from the content
            text = responseText.replace(/```json\n[\s\S]*?\n```/, '');
          }
        }
      }

      // Check for quiz
      else if (responseText.includes('"questions"') &&
               responseText.includes('"options"') &&
               responseText.includes('"correct_answer"')) {

        // Try to extract JSON data
        const jsonMatch = responseText.match(/```json\n([\s\S]*?)\n```/);
        if (jsonMatch && jsonMatch[1]) {
          const jsonData = JSON.parse(jsonMatch[1]);
          if (jsonData.questions && Array.isArray(jsonData.questions)) {
            type = 'quiz';
            data = jsonData;
            // Remove the JSON from the content
            text = responseText.replace(/```json\n[\s\S]*?\n```/, '');
          }
        }
      }
    } catch (error) {
      console.error('Error processing agent response:', error);
    }

    return { type, text, data };
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Send to API
      const response = await chatWithAgent({
        user_input: input,
      });

      // Process the response to detect message type and extract data
      const { type, text, data } = processAgentResponse(response.response);

      // Add agent response
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: text,
        sender: 'agent',
        timestamp: new Date(),
        type: type,
        data: data
      };
      setMessages((prev) => [...prev, agentMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again.',
        sender: 'agent',
        timestamp: new Date(),
        type: 'text'
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Key press handling is now done inline in the Input component

  // Render the appropriate message component based on type
  const renderMessage = (message: Message) => {
    if (message.sender === 'user') {
      return (
        <Box
          p={3}
          borderRadius="lg"
          bg={userBubbleColor}
        >
          <TextMessage content={message.text} />
          <Text fontSize="xs" color={mutedTextColor} textAlign="right" mt={1}>
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </Text>
        </Box>
      );
    }

    // For agent messages, check the type
    const messageBox = (
      <Box
        p={3}
        borderRadius="lg"
        bg={agentBubbleColor}
        width={message.type && message.type !== 'text' ? "100%" : "auto"}
      >
        {message.type === 'learning_path' && message.data ? (
          <Box>
            {message.text && <TextMessage content={message.text} />}
            <LearningPathMessage data={message.data} />
          </Box>
        ) : message.type === 'resources' && message.data ? (
          <Box>
            {message.text && <TextMessage content={message.text} />}
            <ResourcesMessage data={message.data} />
          </Box>
        ) : message.type === 'quiz' && message.data ? (
          <Box>
            {message.text && <TextMessage content={message.text} />}
            <QuizMessage data={message.data} />
          </Box>
        ) : (
          <TextMessage content={message.text} />
        )}
        <Text fontSize="xs" color={mutedTextColor} textAlign="right" mt={1}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </Box>
    );

    return messageBox;
  };

  return (
    <Box
      w="100%"
      h="600px"
      borderWidth="1px"
      borderRadius="lg"
      borderColor={borderColor}
      overflow="hidden"
      bg={bgColor}
      p={4}
      color={textColor}
    >
      <Stack direction="column" h="100%" gap={4}>
        <Box
          flex="1"
          w="100%"
          overflowY="auto"
          px={2}
          py={4}
        >
          {messages.length === 0 ? (
            <Text textAlign="center" color={mutedTextColor}>
              Start a conversation with the Learning Coach
            </Text>
          ) : (
            <Stack direction="column" gap={4} align="stretch">
              {messages.map((message) => (
                <Flex
                  key={message.id}
                  justify={message.sender === 'user' ? 'flex-end' : 'flex-start'}
                  width="100%"
                >
                  {message.sender === 'agent' && (
                    <Box
                      width="32px"
                      height="32px"
                      borderRadius="full"
                      bg="blue.500"
                      mr={2}
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                    >
                      <Text color="white" fontSize="xs">LC</Text>
                    </Box>
                  )}
                  {renderMessage(message)}
                  {message.sender === 'user' && (
                    <Box
                      width="32px"
                      height="32px"
                      borderRadius="full"
                      bg="green.500"
                      ml={2}
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                    >
                      <Text color="white" fontSize="xs">U</Text>
                    </Box>
                  )}
                </Flex>
              ))}
              <div ref={messagesEndRef} />
            </Stack>
          )}
        </Box>
        <HStack w="100%">
          <Input
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            disabled={isLoading}
            bg={useColorModeValue('white', 'gray.700')}
            borderColor={borderColor}
            _placeholder={{ color: mutedTextColor }}
          />
          <Button
            colorScheme="blue"
            onClick={handleSend}
            data-loading={isLoading}
            disabled={isLoading || !input.trim()}
          >
            {isLoading ? "Sending..." : "Send"}
            {!isLoading && <Box as={ArrowUpIcon} ml={2} boxSize="1em" />}
          </Button>
        </HStack>
      </Stack>
    </Box>
  );
};

export default ChatInterface;
