import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/use-toast";
import { usePersonaStore } from "@/store/personaStore";
import { useContentStore } from "@/store/contentStore";
import { AdvancedContentEditor } from "@/components/editor/AdvancedContentEditor";
import { ChatInterface } from "@/components/chat/ChatInterface";
// Define interfaces for form data
interface ContentFormData {
  personaId: string | number;
  contentType: string;
  platform: string;
  topic: string;
  additionalContext: string;
  text: string;
  [key: string]: string | number; // To allow for dynamic access
}

interface ContentGenerateData {
  persona_id: number;
  content_type: string;
  topic: string;
  platform: string;
  additional_context?: string;
  save: boolean;
}

interface ContentCreateData {
  persona_id: number;
  content_type: string;
  text: string;
  platform: string;
  status: string;
}

export function ContentCreate() {
  const navigate = useNavigate();
  const { personas, activePersona, fetchPersonas, isLoading: isLoadingPersonas } = usePersonaStore();
  const { generateContent, createContent } = useContentStore();
  const [isGenerating, setIsGenerating] = useState(false);

  // Fetch personas on component mount
  useEffect(() => {
    fetchPersonas();
  }, [fetchPersonas]);
  const [generatedContent, setGeneratedContent] = useState("");
  const [creationMethod, setCreationMethod] = useState<"ai" | "manual" | "chat">("chat");

  const form = useForm({
    defaultValues: {
      personaId: activePersona?.id || "",
      contentType: "tweet",
      platform: "twitter",
      topic: "",
      additionalContext: "",
      text: "",
    },
  });

  const { toast } = useToast();

  const onSubmitAI = async (data: ContentFormData) => {
    setIsGenerating(true);
    try {
      const requestData: ContentGenerateData = {
        persona_id: Number(data.personaId),
        content_type: data.contentType,
        topic: data.topic,
        platform: data.platform,
        additional_context: data.additionalContext || undefined,
        save: false,
      };

      const response = await generateContent(requestData);
      setGeneratedContent(response.text);
      form.setValue("text", response.text);
      toast({
        title: "Success",
        description: "Content generated successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate content",
        variant: "destructive",
      });
      console.error("Error generating content:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const onSubmitManual = async (data: ContentFormData) => {
    try {
      const createData: ContentCreateData = {
        persona_id: Number(data.personaId),
        content_type: data.contentType,
        text: data.text,
        platform: data.platform,
        status: "draft",
      };

      await createContent(createData);
      toast({
        title: "Success",
        description: "Content created successfully",
      });
      navigate("/content");
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create content",
        variant: "destructive",
      });
      console.error("Error creating content:", error);
    }
  };

  const handleSubmit = (data: ContentFormData) => {
    if (creationMethod === "ai" && !generatedContent) {
      return onSubmitAI(data);
    } else {
      return onSubmitManual(data);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Create Content</h1>
        <Button variant="outline" onClick={() => navigate("/content")}>
          Cancel
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>New Content</CardTitle>
          <CardDescription>Create new content for your persona</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="chat" value={creationMethod} onValueChange={(value) => setCreationMethod(value as "ai" | "manual" | "chat")}>
            <TabsList className="mb-4">
              <TabsTrigger value="chat">Chat</TabsTrigger>
              <TabsTrigger value="ai">Form-Based</TabsTrigger>
              <TabsTrigger value="manual">Manual</TabsTrigger>
            </TabsList>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
                <div className="grid gap-6 sm:grid-cols-2">
                  <FormField
                    control={form.control}
                    name="personaId"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Persona</FormLabel>
                        <Select
                          value={field.value.toString()}
                          onValueChange={field.onChange}
                          disabled={isGenerating || isLoadingPersonas}
                        >
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select a persona" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {isLoadingPersonas ? (
                              <div className="p-2 text-sm text-muted-foreground">Loading personas...</div>
                            ) : personas.length === 0 ? (
                              <div className="p-2 text-sm text-muted-foreground">No personas available</div>
                            ) : (
                              personas.map((persona) => (
                                <SelectItem key={persona.id} value={persona.id.toString()}>
                                  {persona.name}
                                </SelectItem>
                              ))
                            )}
                          </SelectContent>
                        </Select>
                        <FormDescription>
                          Select the persona for this content
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="contentType"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Content Type</FormLabel>
                        <Select
                          value={field.value}
                          onValueChange={field.onChange}
                          disabled={isGenerating}
                        >
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select content type" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="tweet">Tweet</SelectItem>
                            <SelectItem value="thread">Thread</SelectItem>
                            <SelectItem value="post">Post</SelectItem>
                            <SelectItem value="article">Article</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormDescription>
                          Type of content to create
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="platform"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Platform</FormLabel>
                        <Select
                          value={field.value}
                          onValueChange={field.onChange}
                          disabled={isGenerating}
                        >
                          <FormControl>
                            <SelectTrigger>
                              <SelectValue placeholder="Select platform" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="twitter">Twitter</SelectItem>
                            <SelectItem value="linkedin">LinkedIn</SelectItem>
                            <SelectItem value="bluesky">Bluesky</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormDescription>
                          Platform where the content will be published
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <TabsContent value="chat" className="space-y-2 mt-2">
                  <ChatInterface
                    personaId={form.getValues().personaId}
                    contentType={form.getValues().contentType}
                    platform={form.getValues().platform}
                    onGenerateComplete={(content) => {
                      setGeneratedContent(content);
                      form.setValue("text", content);
                    }}
                    onSaveContent={(content) => {
                      form.setValue("text", content);
                      onSubmitManual(form.getValues());
                    }}
                  />
                </TabsContent>

                <TabsContent value="ai" className="space-y-6 mt-6">
                  <FormField
                    control={form.control}
                    name="topic"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Topic</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Enter a topic for the AI to write about"
                            {...field}
                            disabled={isGenerating}
                          />
                        </FormControl>
                        <FormDescription>
                          The main topic or subject for the content
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="additionalContext"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Additional Context (Optional)</FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder="Provide any additional context or specific points to include"
                            className="min-h-[100px]"
                            {...field}
                            disabled={isGenerating}
                          />
                        </FormControl>
                        <FormDescription>
                          Additional information to guide the AI
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {generatedContent && (
                    <FormField
                      control={form.control}
                      name="text"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Generated Content</FormLabel>
                          <FormControl>
                            <AdvancedContentEditor
                              content={field.value}
                              onChange={field.onChange}
                              placeholder="Edit the generated content..."
                              contentType={form.getValues().contentType}
                              platform={form.getValues().platform}
                              personaId={Number(form.getValues().personaId)}
                              personaName={personas.find(p => p.id === Number(form.getValues().personaId))?.name}
                            />
                          </FormControl>
                          <FormDescription>
                            Edit the generated content if needed
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  )}
                </TabsContent>

                <TabsContent value="manual" className="space-y-6 mt-6">
                  <FormField
                    control={form.control}
                    name="text"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Content</FormLabel>
                        <FormControl>
                          <AdvancedContentEditor
                            content={field.value}
                            onChange={field.onChange}
                            placeholder="Write your content here..."
                            contentType={form.getValues().contentType}
                            platform={form.getValues().platform}
                            personaId={Number(form.getValues().personaId)}
                            personaName={personas.find(p => p.id === Number(form.getValues().personaId))?.name}
                          />
                        </FormControl>
                        <FormDescription>
                          The content to be published
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </TabsContent>

                <div className="flex justify-end gap-2">
                  {creationMethod === "ai" && !generatedContent ? (
                    <Button type="submit" disabled={isGenerating || isLoadingPersonas || personas.length === 0}>
                      {isGenerating ? "Generating..." : "Generate Content"}
                    </Button>
                  ) : (
                    <Button type="submit" disabled={isLoadingPersonas || personas.length === 0}>
                      Save as Draft
                    </Button>
                  )}
                </div>
              </form>
            </Form>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
