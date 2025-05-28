import { Card, CardContent, CardDescription } from '@/components/ui/card';
import type {Message} from '../types';

interface MessageItemProps {
  message: Message;
}

const MessageItem = ({ message }: MessageItemProps) => {
  return (
    <Card 
      className={`
        ${message.role === 'assistant' ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'}
        ${message.role === 'assistant' ? 'self-start' : 'self-end'}
        max-w-[80%] border
      `}
    >
      <CardContent className="py-3 px-4">
        <CardDescription className="whitespace-pre-wrap">{message.content}</CardDescription>
        <p className="text-xs text-gray-500 text-right mt-1">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </CardContent>
    </Card>
  );
};

export default MessageItem;
