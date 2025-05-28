import React, { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { getDocument, analyzeDocument, getConversation } from "../services/api";
import type { Message } from "../types";
import { toast } from "sonner";
import { FiSend } from "react-icons/fi";
import ReactMarkdown from "react-markdown";

const Chat = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (documentId) {
      fetchDocument(documentId);
      fetchConversation(documentId);
    }
  }, [documentId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchDocument = async (id: string) => {
    try {
      await getDocument(id);
    } catch (error) {
      console.error("Error fetching document:", error);
      toast.error("Failed to fetch document");
    }
  };

  const fetchConversation = async (id: string) => {
    try {
      const conversation = await getConversation(id);
      const formattedMessages = conversation.map((msg) => ({
        ...msg,
        timestamp: new Date(msg.timestamp),
      }));
      setMessages(formattedMessages);
    } catch (error) {
      console.error("Error fetching conversation:", error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!question.trim() || !documentId) return;

    setIsLoading(true);

    try {
      // Send the question to the API and get both user and assistant messages
      const response = await analyzeDocument(documentId, question);

      // Format the timestamps as Date objects
      const formattedUserMessage = {
        ...response.user_message,
        timestamp: new Date(response.user_message.timestamp),
      };

      const formattedAssistantMessage = {
        ...response.assistant_message,
        timestamp: new Date(response.assistant_message.timestamp),
      };

      // Add both messages to the conversation
      setMessages((prevMessages) => [
        ...prevMessages,
        formattedUserMessage,
        formattedAssistantMessage,
      ]);

      // Clear the question input
      setQuestion("");
    } catch (error) {
      console.error("Error analyzing document:", error);
      toast.error("Please try again later");

      // Add error message
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          id: `user-${Date.now()}`,
          role: "user",
          content: question,
          timestamp: new Date(),
        },
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          content:
            "Sorry, I encountered an error while analyzing your document. Please try again.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-120px)] flex flex-col overflow-hidden">
      <div className="flex-1 flex flex-col w-full min-h-0">
        <div className="flex-1 overflow-y-auto mb-4 p-4 rounded-md bg-gray-50 min-h-0">
          {messages.length === 0 ? (
            <p className="text-center text-gray-500">
              No messages yet. Ask a question about your document.
            </p>
          ) : (
            <div className="flex flex-col gap-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`
                                        p-3 rounded-md max-w-[80%]
                                        ${
                                          message.role === "user"
                                            ? "bg-blue-100 self-end text-right"
                                            : "bg-gray-200 self-start text-left"
                                        }
                                    `}
                >
                  <div className={`flex items-center gap-2 mb-1 ${message.role === 'user' ? 'justify-end' : ''}`}>
                    <Avatar className="h-6 w-6">
                      <AvatarFallback
                        className={`text-xs ${
                          message.role === "user"
                            ? "bg-blue-500 text-white"
                            : "bg-green-500 text-white"
                        }`}
                      >
                        {message.role === "user" ? "U" : "A"}
                      </AvatarFallback>
                    </Avatar>
                    <span className="font-bold text-sm">
                      {message.role === "user" ? "You" : "Assistant"}
                    </span>
                  </div>
                  {message.role === "assistant" ? (
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="flex-shrink-0">
          <form onSubmit={handleSubmit}>
            <div className="flex gap-2">
              <Input
                placeholder="Ask a question about your document..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                disabled={isLoading}
                className="flex-1"
              />
              <Button
                type="submit"
                disabled={!question.trim() || isLoading}
                className="bg-blue-600 hover:bg-blue-700 flex items-center gap-2 flex-shrink-0"
              >
                <FiSend className="h-4 w-4" />
                {isLoading ? "Sending..." : "Send"}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Chat;
