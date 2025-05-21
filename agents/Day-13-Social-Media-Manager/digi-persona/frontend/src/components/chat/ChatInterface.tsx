import { useState, useEffect, useRef } from "react";
import { ChatMessage, ChatMessageProps } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { ContentArtifact } from "../artifacts/ContentArtifact";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AdvancedContentEditor } from "../editor/AdvancedContentEditor";
import { usePersonaStore } from "@/store/personaStore";
import { useContentStore } from "@/store/contentStore";
import { useToast } from "@/components/ui/use-toast";
import { ChatMessage as ChatMessageType } from "@/api/contentService";

interface ChatInterfaceProps {
  personaId: number | string;
  contentType: string;
  platform: string;
  onGenerateComplete?: (content: string) => void;
  onSaveContent?: (content: string) => void;
}

export function ChatInterface({
  personaId,
  contentType,
  platform,
  onGenerateComplete,
  onSaveContent,
}: ChatInterfaceProps) {
  const { personas } = usePersonaStore();
  const { generateContentChat } = useContentStore();
  const { toast } = useToast();
  const persona = personas.find(p => p.id === Number(personaId));

  const [messages, setMessages] = useState<ChatMessageProps[]>([
    {
      role: "system",
      content: `I'm your content creation assistant. Let's create a ${contentType} for ${platform}. What topic would you like to focus on?`,
      timestamp: new Date(),
      name: persona?.name || "Assistant",
      avatar: persona?.avatar,
    },
  ]);

  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<string | null>(null);
  const [editedContent, setEditedContent] = useState<string>("");
  const [activeTab, setActiveTab] = useState<string>("chat");

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Set edited content when generated content changes
  useEffect(() => {
    if (generatedContent) {
      setEditedContent(generatedContent);
    }
  }, [generatedContent]);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: ChatMessageProps = {
      role: "user",
      content,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsGenerating(true);

    try {
      // If this is the first user message, just respond with a follow-up question
      if (messages.filter(m => m.role === "user").length === 0) {
        // Simulate assistant response for the first message
        setTimeout(() => {
          const assistantMessage: ChatMessageProps = {
            role: "assistant",
            content: `Great! I'll create a ${contentType} about "${content}" for ${platform}. Any specific tone or style you'd like me to use?`,
            timestamp: new Date(),
            name: persona?.name || "Assistant",
            avatar: persona?.avatar,
          };
          setMessages(prev => [...prev, assistantMessage]);
          setIsGenerating(false);
        }, 1000);
      } else {
        // For the second message or beyond, generate content using the API
        // Convert messages to the format expected by the API
        const apiMessages: ChatMessageType[] = messages.map(msg => ({
          role: msg.role as "user" | "assistant" | "system",
          content: msg.content,
          timestamp: msg.timestamp ? msg.timestamp.toISOString() : undefined,
        }));

        // Add the latest user message
        apiMessages.push({
          role: "user",
          content,
          timestamp: new Date().toISOString(),
        });

        // Call the content generation API
        const response = await generateContentChat({
          persona_id: Number(personaId),
          content_type: contentType,
          platform: platform,
          messages: apiMessages,
          save: false,
        });

        // Add assistant response to the chat
        const assistantMessage: ChatMessageProps = {
          role: "assistant",
          content: `I've created a ${contentType} for ${platform} based on our conversation. You can view, edit, and save it in the "Generated Content" tab.`,
          timestamp: new Date(),
          name: persona?.name || "Assistant",
          avatar: persona?.avatar,
        };

        setMessages(prev => [...prev, assistantMessage]);
        setGeneratedContent(response.text);
        setActiveTab("content");

        if (onGenerateComplete) {
          onGenerateComplete(response.text);
        }

        toast({
          title: "Content Generated",
          description: "Your content has been generated successfully.",
        });

        setIsGenerating(false);
      }
    } catch (error) {
      console.error("Error generating content:", error);
      setIsGenerating(false);

      toast({
        title: "Error",
        description: "Failed to generate content. Please try again.",
        variant: "destructive",
      });

      // Add error message
      const errorMessage: ChatMessageProps = {
        role: "assistant",
        content: "Sorry, I encountered an error while generating content. Please try again.",
        timestamp: new Date(),
        name: persona?.name || "Assistant",
        avatar: persona?.avatar,
      };

      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleSaveContent = () => {
    if (onSaveContent && editedContent) {
      onSaveContent(editedContent);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Create Content with {persona?.name || "AI"}</CardTitle>
        <CardDescription>
          Chat with your AI assistant to create {contentType} content for {platform}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="chat">Chat</TabsTrigger>
            <TabsTrigger value="content" disabled={!generatedContent}>
              Generated Content
            </TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="space-y-4">
            <div className="h-[400px] overflow-y-auto rounded-md border p-4">
              {messages.map((message, index) => (
                <ChatMessage key={index} {...message} />
              ))}
              <div ref={messagesEndRef} />
            </div>

            <ChatInput
              onSendMessage={handleSendMessage}
              isLoading={isGenerating}
              placeholder="Type your message here..."
            />
          </TabsContent>

          <TabsContent value="content" className="space-y-4">
            {generatedContent && (
              <>
                <ContentArtifact
                  content={generatedContent}
                  platform={platform}
                  contentType={contentType}
                  onSave={handleSaveContent}
                />

                <div className="mt-6">
                  <h3 className="mb-2 text-lg font-medium">Edit Content</h3>
                  <AdvancedContentEditor
                    content={editedContent}
                    onChange={setEditedContent}
                    contentType={contentType}
                    platform={platform}
                    personaId={Number(personaId)}
                    personaName={persona?.name}
                  />

                  <div className="mt-4 flex justify-end">
                    <button
                      className="rounded-md bg-primary px-4 py-2 text-primary-foreground"
                      onClick={handleSaveContent}
                    >
                      Save as Draft
                    </button>
                  </div>
                </div>
              </>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
