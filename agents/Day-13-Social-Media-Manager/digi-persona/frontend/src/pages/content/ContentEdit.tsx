import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/components/ui/use-toast";
import { usePersonaStore } from "@/store/personaStore";
import { useContentStore } from "@/store/contentStore";
import { Content, ContentUpdate } from "@/api/contentService";
import apiClient from "@/api/client";
import { Spinner } from "@/components/ui/spinner";
import { AdvancedContentEditor } from "@/components/editor/AdvancedContentEditor";

// Define interfaces for form data
interface ContentEditFormData {
  personaId: string | number;
  contentType: string;
  platform: string;
  text: string;
}

export function ContentEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { personas, fetchPersonas, isLoading: isLoadingPersonas } = usePersonaStore();
  const { updateContent } = useContentStore();
  const [content, setContent] = useState<Content | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fetchCount, setFetchCount] = useState(0);
  const { toast } = useToast();

  const form = useForm<ContentEditFormData>({
    defaultValues: {
      personaId: "",
      contentType: "tweet",
      platform: "twitter",
      text: "",
    },
  });

  // Fetch personas on component mount
  useEffect(() => {
    fetchPersonas();
  }, [fetchPersonas]); // Re-run when fetchPersonas changes

  // Fetch content data when ID changes
  useEffect(() => {
    // Skip if we've already fetched this content
    if (content && content.id === Number(id)) {
      return;
    }

    // Skip if we've already tried to fetch this content
    if (fetchCount > 0) {
      return;
    }

    const fetchContentData = async () => {
      if (!id) {
        setError("Content ID is missing");
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);
      setFetchCount(prev => prev + 1);

      try {
        console.log(`[ContentEdit] Fetching content with ID: ${id}`);
        const response = await apiClient.get(`/content/${id}`);
        const fetchedContent = response.data;
        console.log('[ContentEdit] Content fetched successfully');

        setContent(fetchedContent);
        // Set form default values after fetching content
        form.reset({
          personaId: fetchedContent.persona_id.toString(),
          contentType: fetchedContent.content_type,
          platform: fetchedContent.platform,
          text: fetchedContent.text,
        });
      } catch (err) {
        console.error("[ContentEdit] Error fetching content data:", err);
        setError("Failed to load content data.");
        toast({
          title: "Error",
          description: "Failed to load content data.",
          variant: "destructive"
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchContentData();
  }, [id, form, toast, content, fetchCount]);

  const onSubmit = async (data: ContentEditFormData) => {
    if (!id) return;
    setIsSubmitting(true);
    try {
      const updateData: ContentUpdate = {
        content_type: data.contentType,
        text: data.text,
        platform: data.platform,
        // We don't update personaId here, assuming it's fixed once created
      };
      await updateContent(Number(id), updateData);
      toast({
        title: "Success",
        description: "Content updated successfully",
        variant: "default"
      });
      navigate(`/content/${id}`); // Navigate back to detail view
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update content",
        variant: "destructive"
      });
      console.error("Error updating content:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading || isLoadingPersonas) {
    return (
      <div className="flex justify-center items-center h-64">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">{error}</div>;
  }

  if (!content) {
    return <div className="text-center p-4">Content not found.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Edit Content</h1>
        <Button variant="outline" onClick={() => navigate(`/content/${id}`)}>
          Cancel
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Edit Content Details</CardTitle>
          <CardDescription>Modify the content for your persona</CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
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
                        disabled // Persona cannot be changed during edit
                      >
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select a persona" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {personas.map((persona) => (
                            <SelectItem key={persona.id} value={persona.id.toString()}>
                              {persona.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormDescription>
                        The persona associated with this content (cannot be changed).
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
                        disabled={isSubmitting}
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
                        Type of content
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
                        disabled={isSubmitting}
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

              <FormField
                control={form.control}
                name="text"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Content Text</FormLabel>
                    <FormControl>
                      <AdvancedContentEditor
                        content={field.value}
                        onChange={field.onChange}
                        placeholder="Edit your content..."
                        contentType={form.getValues().contentType}
                        platform={form.getValues().platform}
                        personaId={Number(form.getValues().personaId)}
                        personaName={personas.find(p => p.id === Number(form.getValues().personaId))?.name}
                      />
                    </FormControl>
                    <FormDescription>
                      The main text of the content
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex justify-end gap-2">
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}