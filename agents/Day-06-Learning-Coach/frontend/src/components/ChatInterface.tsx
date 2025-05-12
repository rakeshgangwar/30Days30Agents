import { useState, useRef, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Input,
  Button,
  Text,
  Avatar,
  Flex,
  Spinner
} from '@chakra-ui/react';
import { useColorModeValue } from './ui/color-mode';
import { chatWithAgent } from '../api/agent';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
}

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const bgColor = useColorModeValue('gray.50', 'gray.700');
  const userBubbleColor = useColorModeValue('blue.100', 'blue.700');
  const agentBubbleColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Send to API
      const response = await chatWithAgent({
        user_input: input,
      });

      // Add agent response
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        sender: 'agent',
        timestamp: new Date(),
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
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box
      w="100%"
      h="600px"
      borderWidth="1px"
      borderRadius="lg"
      overflow="hidden"
      bg={bgColor}
      p={4}
    >
      <VStack h="100%" spacing={4}>
        <Box
          flex="1"
          w="100%"
          overflowY="auto"
          px={2}
          py={4}
        >
          {messages.length === 0 ? (
            <Text textAlign="center" color="gray.500">
              Start a conversation with the Learning Coach
            </Text>
          ) : (
            <VStack spacing={4} align="stretch">
              {messages.map((message) => (
                <Flex
                  key={message.id}
                  justify={message.sender === 'user' ? 'flex-end' : 'flex-start'}
                >
                  {message.sender === 'agent' && (
                    <Avatar size="sm" name="Learning Coach" mr={2} />
                  )}
                  <Box
                    maxW="70%"
                    p={3}
                    borderRadius="lg"
                    bg={message.sender === 'user' ? userBubbleColor : agentBubbleColor}
                  >
                    <Text>{message.text}</Text>
                    <Text fontSize="xs" color="gray.500" textAlign="right" mt={1}>
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </Text>
                  </Box>
                  {message.sender === 'user' && (
                    <Avatar size="sm" name="User" ml={2} />
                  )}
                </Flex>
              ))}
              <div ref={messagesEndRef} />
            </VStack>
          )}
        </Box>
        <HStack w="100%">
          <Input
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
          />
          <Button
            colorScheme="blue"
            onClick={handleSend}
            isLoading={isLoading}
            loadingText="Sending"
            disabled={isLoading || !input.trim()}
          >
            Send
          </Button>
        </HStack>
      </VStack>
    </Box>
  );
};

export default ChatInterface;
