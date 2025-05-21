import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { CalendarIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { useToast } from "@/components/ui/use-toast";
import { usePersonaStore } from "@/store/personaStore";
import { useContentStore } from "@/store/contentStore";
import { Spinner } from "@/components/ui/spinner";

export function ContentSchedule() {
  const navigate = useNavigate();
  const { id: contentIdFromUrl } = useParams<{ id?: string }>();
  const { personas, fetchPersonas, isLoading: isLoadingPersonas } = usePersonaStore();
  const { contentItems, fetchContentItems, scheduleContent, scheduleBatch, generateAndSchedule, generateBatchAndSchedule } = useContentStore();

  // Fetch personas and content on component mount
  useEffect(() => {
    fetchPersonas();
    fetchContentItems();
  }, [fetchPersonas, fetchContentItems]);
  const [isLoading, setIsLoading] = useState(false);
  const [scheduleType, setScheduleType] = useState<"single" | "batch" | "generate" | "generate-batch">(contentIdFromUrl ? "single" : "single");
  const { toast } = useToast();

  // Define types for the form
  interface ScheduleFormData {
    personaId: string;
    contentId: string;
    contentIds: string;
    contentType: string;
    platform: string;
    topic: string;
    topics: string;
    scheduledTime: Date;
    startTime: Date;
    intervalMinutes: number;
    additionalContext: string;
    useCelery: boolean;
  }

  // Type for schedule type
  type ScheduleType = "single" | "batch" | "generate" | "generate-batch";

  const form = useForm<ScheduleFormData>({
    defaultValues: {
      personaId: "",
      contentId: contentIdFromUrl || "",
      contentIds: "",
      contentType: "tweet",
      platform: "twitter",
      topic: "",
      topics: "",
      scheduledTime: new Date(),
      startTime: new Date(),
      intervalMinutes: 60,
      additionalContext: "",
      useCelery: true,
    },
  });

  // Effect to update form when content items are loaded and we have a content ID from URL
  useEffect(() => {
    if (contentIdFromUrl && contentItems.length > 0) {
      // Find the content item with the matching ID
      const contentItem = contentItems.find(item => item.id.toString() === contentIdFromUrl);

      if (contentItem) {
        // Set the content ID in the form
        form.setValue("contentId", contentIdFromUrl);

        // If the content has a persona, set that too
        if (contentItem.persona_id) {
          form.setValue("personaId", contentItem.persona_id.toString());
        }

        // If the content has a platform, set that too
        if (contentItem.platform) {
          form.setValue("platform", contentItem.platform);
        }
      }
    }
  }, [contentItems, contentIdFromUrl, form]);

  const onSubmit = async (data: ScheduleFormData) => {
    setIsLoading(true);
    try {
      // Variables for case blocks
      let contentIdsArray: number[] = [];
      let topicsArray: string[] = [];

      switch (scheduleType) {
        case "single":
          await scheduleContent(Number(data.contentId), {
            scheduled_time: data.scheduledTime.toISOString(),
          });
          toast({
            title: "Success",
            description: "Content scheduled successfully",
          });
          break;

        case "batch":
          // Convert comma-separated IDs to array of numbers
          contentIdsArray = data.contentIds
            .split(",")
            .map((id) => id.trim())
            .filter((id) => id)
            .map((id) => Number(id));

          await scheduleBatch({
            content_ids: contentIdsArray,
            start_time: data.startTime.toISOString(),
            interval_minutes: Number(data.intervalMinutes),
            use_celery: data.useCelery,
          });
          toast({
            title: "Success",
            description: "Batch content scheduled successfully",
          });
          break;

        case "generate":
          await generateAndSchedule({
            persona_id: Number(data.personaId),
            content_type: data.contentType,
            topic: data.topic,
            platform: data.platform,
            scheduled_time: data.scheduledTime.toISOString(),
            additional_context: data.additionalContext || undefined,
            use_celery: data.useCelery,
          });
          toast({
            title: "Success",
            description: "Content generated and scheduled successfully",
          });
          break;

        case "generate-batch":
          // Convert comma-separated topics to array
          topicsArray = data.topics
            .split(",")
            .map((topic) => topic.trim())
            .filter((topic) => topic);

          await generateBatchAndSchedule({
            persona_id: Number(data.personaId),
            content_type: data.contentType,
            topics: topicsArray,
            platform: data.platform,
            start_time: data.startTime.toISOString(),
            interval_minutes: Number(data.intervalMinutes),
            additional_context: data.additionalContext || undefined,
            use_celery: data.useCelery,
          });
          toast({
            title: "Success",
            description: "Batch content generated and scheduled successfully",
          });
          break;
      }

      // Navigate to calendar view
      navigate("/content/calendar");
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to schedule content",
        variant: "destructive",
      });
      console.error("Error scheduling content:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Schedule Content</h1>
      </div>

      <Tabs value={scheduleType} onValueChange={(value) => setScheduleType(value as ScheduleType)}>
        <TabsList className="grid grid-cols-4 w-full max-w-md">
          <TabsTrigger value="single">Single</TabsTrigger>
          <TabsTrigger value="batch">Batch</TabsTrigger>
          <TabsTrigger value="generate">Generate</TabsTrigger>
          <TabsTrigger value="generate-batch">Generate Batch</TabsTrigger>
        </TabsList>

        <Card className="mt-4">
          <CardHeader>
            <CardTitle>
              {scheduleType === "single" && "Schedule Single Content"}
              {scheduleType === "batch" && "Schedule Batch Content"}
              {scheduleType === "generate" && "Generate and Schedule Content"}
              {scheduleType === "generate-batch" && "Generate and Schedule Batch Content"}
            </CardTitle>
            <CardDescription>
              {scheduleType === "single" && "Schedule an existing content item for posting"}
              {scheduleType === "batch" && "Schedule multiple content items with regular intervals"}
              {scheduleType === "generate" && "Generate new content and schedule it for posting"}
              {scheduleType === "generate-batch" && "Generate multiple content items and schedule them with regular intervals"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                {/* Single Content Scheduling */}
                {scheduleType === "single" && (
                  <>
                    <FormField
                      control={form.control}
                      name="contentId"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Content ID</FormLabel>
                          <FormControl>
                            <Select onValueChange={field.onChange} value={field.value.toString()}>
                              <SelectTrigger>
                                <SelectValue placeholder="Select content" />
                              </SelectTrigger>
                              <SelectContent>
                                {contentItems.map((content) => (
                                  <SelectItem key={content.id} value={content.id.toString()}>
                                    {content.id} - {content.text.substring(0, 30)}...
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </FormControl>
                          <FormDescription>Select the content to schedule</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="scheduledTime"
                      render={({ field }) => (
                        <FormItem className="flex flex-col">
                          <FormLabel>Scheduled Time</FormLabel>
                          <Popover>
                            <PopoverTrigger asChild>
                              <FormControl>
                                <Button
                                  variant={"outline"}
                                  className={cn(
                                    "w-full pl-3 text-left font-normal",
                                    !field.value && "text-muted-foreground"
                                  )}
                                >
                                  {field.value ? (
                                    format(field.value, "PPP 'at' p")
                                  ) : (
                                    <span>Pick a date</span>
                                  )}
                                  <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                                </Button>
                              </FormControl>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0" align="start">
                              <Calendar
                                mode="single"
                                selected={field.value}
                                onSelect={field.onChange}
                                initialFocus
                              />
                              <div className="p-3 border-t border-border">
                                <Input
                                  type="time"
                                  onChange={(e) => {
                                    const [hours, minutes] = e.target.value.split(':').map(Number);
                                    const newDate = new Date(field.value);
                                    newDate.setHours(hours, minutes);
                                    field.onChange(newDate);
                                  }}
                                  defaultValue={format(field.value, "HH:mm")}
                                />
                              </div>
                            </PopoverContent>
                          </Popover>
                          <FormDescription>When to post the content</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </>
                )}

                {/* Batch Content Scheduling */}
                {scheduleType === "batch" && (
                  <>
                    <FormField
                      control={form.control}
                      name="contentIds"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Content IDs</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Enter comma-separated content IDs (e.g., 1, 2, 3)"
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>Enter the IDs of the content items to schedule</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="startTime"
                      render={({ field }) => (
                        <FormItem className="flex flex-col">
                          <FormLabel>Start Time</FormLabel>
                          <Popover>
                            <PopoverTrigger asChild>
                              <FormControl>
                                <Button
                                  variant={"outline"}
                                  className={cn(
                                    "w-full pl-3 text-left font-normal",
                                    !field.value && "text-muted-foreground"
                                  )}
                                >
                                  {field.value ? (
                                    format(field.value, "PPP 'at' p")
                                  ) : (
                                    <span>Pick a date</span>
                                  )}
                                  <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                                </Button>
                              </FormControl>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0" align="start">
                              <Calendar
                                mode="single"
                                selected={field.value}
                                onSelect={field.onChange}
                                initialFocus
                              />
                              <div className="p-3 border-t border-border">
                                <Input
                                  type="time"
                                  onChange={(e) => {
                                    const [hours, minutes] = e.target.value.split(':').map(Number);
                                    const newDate = new Date(field.value);
                                    newDate.setHours(hours, minutes);
                                    field.onChange(newDate);
                                  }}
                                  defaultValue={format(field.value, "HH:mm")}
                                />
                              </div>
                            </PopoverContent>
                          </Popover>
                          <FormDescription>When to post the first content</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="intervalMinutes"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Interval (minutes)</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              min="1"
                              {...field}
                              onChange={(e) => field.onChange(parseInt(e.target.value))}
                            />
                          </FormControl>
                          <FormDescription>Minutes between each post</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </>
                )}

                {/* Generate and Schedule Content */}
                {scheduleType === "generate" && (
                  <>
                    <FormField
                      control={form.control}
                      name="personaId"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Persona</FormLabel>
                          <FormControl>
                            <Select onValueChange={field.onChange} value={field.value.toString()}>
                              <SelectTrigger>
                                <SelectValue placeholder="Select persona" />
                              </SelectTrigger>
                              <SelectContent>
                                {personas.map((persona) => (
                                  <SelectItem key={persona.id} value={persona.id.toString()}>
                                    {persona.name}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </FormControl>
                          <FormDescription>Select the persona to generate content for</FormDescription>
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
                          <FormControl>
                            <Select onValueChange={field.onChange} value={field.value}>
                              <SelectTrigger>
                                <SelectValue placeholder="Select content type" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="tweet">Tweet</SelectItem>
                                <SelectItem value="thread">Thread</SelectItem>
                                <SelectItem value="post">Post</SelectItem>
                                <SelectItem value="article">Article</SelectItem>
                              </SelectContent>
                            </Select>
                          </FormControl>
                          <FormDescription>Type of content to generate</FormDescription>
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
                          <FormControl>
                            <Select onValueChange={field.onChange} value={field.value}>
                              <SelectTrigger>
                                <SelectValue placeholder="Select platform" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="twitter">Twitter</SelectItem>
                                <SelectItem value="linkedin">LinkedIn</SelectItem>
                                <SelectItem value="bluesky">Bluesky</SelectItem>
                              </SelectContent>
                            </Select>
                          </FormControl>
                          <FormDescription>Platform to generate content for</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="topic"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Topic</FormLabel>
                          <FormControl>
                            <Input placeholder="Enter a topic" {...field} />
                          </FormControl>
                          <FormDescription>Topic to generate content about</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="additionalContext"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Additional Context</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Enter additional context for generation"
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>Additional context for content generation</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="scheduledTime"
                      render={({ field }) => (
                        <FormItem className="flex flex-col">
                          <FormLabel>Scheduled Time</FormLabel>
                          <Popover>
                            <PopoverTrigger asChild>
                              <FormControl>
                                <Button
                                  variant={"outline"}
                                  className={cn(
                                    "w-full pl-3 text-left font-normal",
                                    !field.value && "text-muted-foreground"
                                  )}
                                >
                                  {field.value ? (
                                    format(field.value, "PPP 'at' p")
                                  ) : (
                                    <span>Pick a date</span>
                                  )}
                                  <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                                </Button>
                              </FormControl>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0" align="start">
                              <Calendar
                                mode="single"
                                selected={field.value}
                                onSelect={field.onChange}
                                initialFocus
                              />
                              <div className="p-3 border-t border-border">
                                <Input
                                  type="time"
                                  onChange={(e) => {
                                    const [hours, minutes] = e.target.value.split(':').map(Number);
                                    const newDate = new Date(field.value);
                                    newDate.setHours(hours, minutes);
                                    field.onChange(newDate);
                                  }}
                                  defaultValue={format(field.value, "HH:mm")}
                                />
                              </div>
                            </PopoverContent>
                          </Popover>
                          <FormDescription>When to post the content</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </>
                )}

                {/* Generate Batch and Schedule Content */}
                {scheduleType === "generate-batch" && (
                  <>
                    <FormField
                      control={form.control}
                      name="personaId"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Persona</FormLabel>
                          <FormControl>
                            <Select onValueChange={field.onChange} value={field.value.toString()}>
                              <SelectTrigger>
                                <SelectValue placeholder="Select persona" />
                              </SelectTrigger>
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
                          </FormControl>
                          <FormDescription>Select the persona to generate content for</FormDescription>
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
                          <FormControl>
                            <Select onValueChange={field.onChange} value={field.value}>
                              <SelectTrigger>
                                <SelectValue placeholder="Select content type" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="tweet">Tweet</SelectItem>
                                <SelectItem value="thread">Thread</SelectItem>
                                <SelectItem value="post">Post</SelectItem>
                                <SelectItem value="article">Article</SelectItem>
                              </SelectContent>
                            </Select>
                          </FormControl>
                          <FormDescription>Type of content to generate</FormDescription>
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
                          <FormControl>
                            <Select onValueChange={field.onChange} value={field.value}>
                              <SelectTrigger>
                                <SelectValue placeholder="Select platform" />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="twitter">Twitter</SelectItem>
                                <SelectItem value="linkedin">LinkedIn</SelectItem>
                                <SelectItem value="bluesky">Bluesky</SelectItem>
                              </SelectContent>
                            </Select>
                          </FormControl>
                          <FormDescription>Platform to generate content for</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="topics"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Topics</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Enter comma-separated topics (e.g., AI trends, machine learning, data science)"
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>Topics to generate content about</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="additionalContext"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Additional Context</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Enter additional context for generation"
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>Additional context for content generation</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="startTime"
                      render={({ field }) => (
                        <FormItem className="flex flex-col">
                          <FormLabel>Start Time</FormLabel>
                          <Popover>
                            <PopoverTrigger asChild>
                              <FormControl>
                                <Button
                                  variant={"outline"}
                                  className={cn(
                                    "w-full pl-3 text-left font-normal",
                                    !field.value && "text-muted-foreground"
                                  )}
                                >
                                  {field.value ? (
                                    format(field.value, "PPP 'at' p")
                                  ) : (
                                    <span>Pick a date</span>
                                  )}
                                  <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                                </Button>
                              </FormControl>
                            </PopoverTrigger>
                            <PopoverContent className="w-auto p-0" align="start">
                              <Calendar
                                mode="single"
                                selected={field.value}
                                onSelect={field.onChange}
                                initialFocus
                              />
                              <div className="p-3 border-t border-border">
                                <Input
                                  type="time"
                                  onChange={(e) => {
                                    const [hours, minutes] = e.target.value.split(':').map(Number);
                                    const newDate = new Date(field.value);
                                    newDate.setHours(hours, minutes);
                                    field.onChange(newDate);
                                  }}
                                  defaultValue={format(field.value, "HH:mm")}
                                />
                              </div>
                            </PopoverContent>
                          </Popover>
                          <FormDescription>When to post the first content</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="intervalMinutes"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Interval (minutes)</FormLabel>
                          <FormControl>
                            <Input
                              type="number"
                              min="1"
                              {...field}
                              onChange={(e) => field.onChange(parseInt(e.target.value))}
                            />
                          </FormControl>
                          <FormDescription>Minutes between each post</FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </>
                )}

                {/* Background Processing Option */}
                {(scheduleType === "batch" || scheduleType === "generate" || scheduleType === "generate-batch") && (
                  <FormField
                    control={form.control}
                    name="useCelery"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                        <FormControl>
                          <input
                            type="checkbox"
                            checked={field.value}
                            onChange={(e) => field.onChange(e.target.checked)}
                            className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                          />
                        </FormControl>
                        <div className="space-y-1 leading-none">
                          <FormLabel>Use Background Processing</FormLabel>
                          <FormDescription>
                            Process the request in the background (recommended for batch operations)
                          </FormDescription>
                        </div>
                      </FormItem>
                    )}
                  />
                )}

                <Button type="submit" disabled={isLoading} className="w-full">
                  {isLoading ? (
                    <>
                      <Spinner className="mr-2 h-4 w-4" />
                      Processing...
                    </>
                  ) : (
                    "Schedule Content"
                  )}
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </Tabs>
    </div>
  );
}
