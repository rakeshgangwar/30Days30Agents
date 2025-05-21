import { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/use-toast";
import { useContentStore } from "@/store/contentStore";
import { usePersonaStore } from "@/store/personaStore";
import { Content } from "@/api/contentService";
import apiClient from "@/api/client";

export function ContentDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { personas, fetchPersonas } = usePersonaStore();
  const { updateContent, deleteContent } = useContentStore();
  const [content, setContent] = useState<Content | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fetchCount, setFetchCount] = useState(0);

  // Effect to fetch personas once when component mounts
  useEffect(() => {
    fetchPersonas();
  }, [fetchPersonas]); // Only re-run when fetchPersonas changes

  // One-time effect to fetch content when component mounts or ID changes
  useEffect(() => {
    // Skip if we've already fetched this content
    if (content && content.id === Number(id)) {
      return;
    }

    // Skip if we've already tried to fetch this content
    if (fetchCount > 0) {
      return;
    }

    const fetchContent = async () => {
      if (!id) {
        setError("Content ID is missing");
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);
      setFetchCount(prev => prev + 1);

      try {
        console.log(`[ContentDetail] Fetching content with ID: ${id}`);
        const response = await apiClient.get(`/content/${id}`);
        console.log('[ContentDetail] Content fetched successfully');
        setContent(response.data);
      } catch (err) {
        console.error("[ContentDetail] Error fetching content:", err);
        setError("Failed to load content details.");
        toast({
          title: "Error",
          description: "Failed to load content details.",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchContent();
  }, [id, toast, content, fetchCount]); // Dependencies

  const getPersona = (personaId: number) => {
    return personas.find(p => p.id === personaId);
  };

  const handleDelete = async () => {
    if (!content) return;
    try {
      await deleteContent(content.id);
      toast({
        title: "Success",
        description: "Content deleted successfully.",
      });
      navigate("/content");
    } catch {
      // Error already shown in toast
      toast({
        title: "Error",
        description: "Failed to delete content.",
        variant: "destructive",
      });
    }
  };

  const handleApprove = async () => {
    if (!content) return;
    try {
      const updated = await updateContent(content.id, { status: 'approved' });
      setContent(updated);
      toast({
        title: "Success",
        description: "Content approved.",
      });
    } catch {
      toast({
        title: "Error",
        description: "Failed to approve content.",
        variant: "destructive",
      });
    }
  };

  const handleSchedule = () => {
    if (!content) return;
    navigate(`/content/${content.id}/schedule`);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleString();
  };

  const persona = content ? getPersona(content.persona_id) : null;

  if (isLoading) {
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
        <h1 className="text-3xl font-bold">Content Details</h1>
        <div className="flex gap-2">
          <Button variant="outline" asChild>
            <Link to="/content">Back to List</Link>
          </Button>
          <Button asChild>
            <Link to={`/content/${content.id}/edit`}>Edit</Link>
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>"{content.text.substring(0, 50)}..."</CardTitle>
          <CardDescription>
            {content.content_type.charAt(0).toUpperCase() + content.content_type.slice(1)} for {content.platform.charAt(0).toUpperCase() + content.platform.slice(1)}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2">
            <Avatar className="h-8 w-8">
              <AvatarImage src={persona?.avatar_url || "/avatars/default.png"} alt={persona?.name} />
              <AvatarFallback>{persona?.name?.substring(0, 2) || 'P'}</AvatarFallback>
            </Avatar>
            <div>
              <div className="font-medium">{persona?.name || "Unknown Persona"}</div>
              <div className="text-sm text-muted-foreground">Persona</div>
            </div>
          </div>
          <div>
            <h3 className="font-medium mb-1">Content Text</h3>
            <div className="rounded-md border p-4 bg-muted/40">
              <p className="whitespace-pre-line">{content.text}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h3 className="font-medium">Status</h3>
              <p className="text-muted-foreground">{content.status.charAt(0).toUpperCase() + content.status.slice(1)}</p>
            </div>
            <div>
              <h3 className="font-medium">Scheduled Time</h3>
              <p className="text-muted-foreground">{formatDate(content.scheduled_time)}</p>
            </div>
            <div>
              <h3 className="font-medium">Published Time</h3>
              <p className="text-muted-foreground">{formatDate(content.published_time)}</p>
            </div>
            <div>
              <h3 className="font-medium">Created At</h3>
              <p className="text-muted-foreground">{formatDate(content.created_at)}</p>
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-4 border-t">
            {content.status === 'draft' && (
              <Button variant="outline" onClick={handleApprove}>Approve</Button>
            )}
            {content.status === 'approved' && (
              <Button variant="outline" onClick={handleSchedule}>Schedule</Button>
            )}
             {content.status === 'scheduled' && (
              <Button variant="outline" onClick={handleSchedule}>Reschedule</Button>
            )}
            <Button variant="destructive" onClick={handleDelete}>Delete</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}