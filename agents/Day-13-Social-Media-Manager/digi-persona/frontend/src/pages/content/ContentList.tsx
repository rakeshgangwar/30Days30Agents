import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

import { usePersonaStore } from "@/store/personaStore";
import { useContentStore } from "@/store/contentStore";

export function ContentList() {
  const [searchParams] = useSearchParams();
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [personaFilter, setPersonaFilter] = useState("all");
  const [platformFilter, setPlatformFilter] = useState("all");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [contentToDelete, setContentToDelete] = useState<number | null>(null);
  const { personas } = usePersonaStore();
  const { contentItems, fetchContentItems, deleteContent, isLoading } = useContentStore();

  // Check for personaId in URL parameters when component mounts
  useEffect(() => {
    const personaIdParam = searchParams.get("personaId");
    if (personaIdParam) {
      setPersonaFilter(personaIdParam);
    }
  }, [searchParams]);

  // No need for cleanup effect as cancelToken is now handled in the store

  // Fetch content when component mounts or filters change
  useEffect(() => {
    // Add a debounce to prevent rapid requests
    const debounceTimeout = setTimeout(() => {
      const params: {
        persona_id?: number;
        platform?: string;
        status?: string;
        skip?: number;
        limit?: number;
      } = {
        // Always set a reasonable limit to prevent excessive data fetching
        limit: 20
      };

      if (personaFilter !== "all") {
        params.persona_id = parseInt(personaFilter);
      }

      if (platformFilter !== "all") {
        params.platform = platformFilter.toLowerCase();
      }

      if (statusFilter !== "all") {
        params.status = statusFilter;
      }

      fetchContentItems(params);
    }, 300); // 300ms debounce

    // Cleanup function to clear the timeout
    return () => clearTimeout(debounceTimeout);
  }, [personaFilter, platformFilter, statusFilter, fetchContentItems]);

  // Create an interface for our processed content
  interface ProcessedContent {
    id: number;
    title: string;
    text: string;
    personaId: number;
    personaName: string;
    personaAvatar: string;
    platform: string;
    contentType: string;
    status: string;
    scheduledTime: string | null;
    publishedTime: string | null;
    engagement: {
      likes: number;
      comments: number;
      shares: number;
    } | null;
  }

  // Process content for display with persona information
  const processedContent: ProcessedContent[] = contentItems.map(content => {
    const persona = personas.find(p => p.id === content.persona_id);
    const firstSentence = content.text.split(/[.!?]\s/)[0];
    const title = firstSentence.length > 50 ? firstSentence.substring(0, 47) + '...' : firstSentence;

    return {
      id: content.id,
      title,
      text: content.text,
      personaId: content.persona_id,
      personaName: persona?.name || "Unknown",
      personaAvatar: "/avatars/default.png", // Use default avatar
      platform: content.platform.charAt(0).toUpperCase() + content.platform.slice(1),
      contentType: content.content_type.charAt(0).toUpperCase() + content.content_type.slice(1),
      status: content.status,
      scheduledTime: content.scheduled_time,
      publishedTime: content.published_time,
      engagement: null // We don't have engagement data in the API yet
    };
  });

  const filteredContent = processedContent.filter(content => {
    // Search filter
    const matchesSearch =
      content.text.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesSearch;
  });

  const handleDeleteClick = (contentId: number) => {
    setContentToDelete(contentId);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (contentToDelete) {
      try {
        await deleteContent(contentToDelete);
        setDeleteDialogOpen(false);
        setContentToDelete(null);
      } catch (error) {
        console.error("Failed to delete content:", error);
      }
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case "published":
        return "bg-green-100 text-green-800";
      case "scheduled":
        return "bg-blue-100 text-blue-800";
      case "draft":
        return "bg-gray-100 text-gray-800";
      case "pending_review":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Content</h1>
        <Button asChild>
          <Link to="/content/new">Create Content</Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Content Management</CardTitle>
          <CardDescription>Create, edit, and manage content across all platforms</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <Input
                placeholder="Search content..."
                className="sm:max-w-xs"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <div className="flex flex-wrap gap-4">
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Statuses</SelectItem>
                    <SelectItem value="published">Published</SelectItem>
                    <SelectItem value="scheduled">Scheduled</SelectItem>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="pending_review">Pending Review</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={personaFilter} onValueChange={setPersonaFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Filter by persona" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Personas</SelectItem>
                    {personas.map((persona) => (
                      <SelectItem key={persona.id} value={persona.id.toString()}>
                        {persona.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select value={platformFilter} onValueChange={setPlatformFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Filter by platform" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Platforms</SelectItem>
                    <SelectItem value="Twitter">Twitter</SelectItem>
                    <SelectItem value="LinkedIn">LinkedIn</SelectItem>
                    <SelectItem value="Bluesky">Bluesky</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Tabs defaultValue="list" className="mt-6">
              <TabsList>
                <TabsTrigger value="list">List View</TabsTrigger>
                <TabsTrigger value="calendar">Calendar View</TabsTrigger>
              </TabsList>
              <TabsContent value="list" className="mt-4">
                {isLoading ? (
                  <div className="flex justify-center items-center py-12">
                    <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mr-2"></div>
                    <p>Loading content...</p>
                  </div>
                ) : filteredContent.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-muted-foreground">No content found. Try adjusting your filters or create new content.</p>
                    <Button asChild className="mt-4">
                      <Link to="/content/new">Create Content</Link>
                    </Button>
                  </div>
                ) : (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-[30%]">Content</TableHead>
                          <TableHead className="w-[15%]">Persona</TableHead>
                          <TableHead className="w-[10%]">Platform</TableHead>
                          <TableHead className="w-[10%]">Status</TableHead>
                          <TableHead className="w-[15%]">Published/Scheduled</TableHead>
                          <TableHead className="w-[10%]">Engagement</TableHead>
                          <TableHead className="text-right w-[10%]">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredContent.map((content) => (
                          <TableRow key={content.id}>
                            <TableCell className="max-w-0">
                              <div className="max-w-[250px]">
                                <div className="font-medium truncate">{content.title}</div>
                                <div className="text-sm text-muted-foreground line-clamp-2 break-words">{content.text}</div>
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center gap-2">
                                <Avatar className="h-6 w-6">
                                  <AvatarImage src={content.personaAvatar} alt={content.personaName} />
                                  <AvatarFallback>{content.personaName.substring(0, 2)}</AvatarFallback>
                                </Avatar>
                                <span>{content.personaName}</span>
                              </div>
                            </TableCell>
                            <TableCell>{content.platform}</TableCell>
                            <TableCell>
                              <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${getStatusBadgeClass(content.status)}`}>
                                {content.status.replace("_", " ").charAt(0).toUpperCase() + content.status.replace("_", " ").slice(1)}
                              </div>
                            </TableCell>
                            <TableCell>
                              {content.publishedTime ? formatDate(content.publishedTime) :
                               content.scheduledTime ? formatDate(content.scheduledTime) : "N/A"}
                            </TableCell>
                            <TableCell>
                              {content.engagement ? (
                                <div className="text-sm">
                                  <span className="mr-2">👍 {content.engagement.likes || 0}</span>
                                  <span className="mr-2">💬 {content.engagement.comments || 0}</span>
                                  <span>🔄 {content.engagement.shares || 0}</span>
                                </div>
                              ) : "N/A"}
                            </TableCell>
                            <TableCell className="text-right">
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button variant="ghost" size="icon">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                      <circle cx="12" cy="12" r="1" />
                                      <circle cx="12" cy="5" r="1" />
                                      <circle cx="12" cy="19" r="1" />
                                    </svg>
                                    <span className="sr-only">More options</span>
                                  </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end">
                                  <DropdownMenuLabel>Actions</DropdownMenuLabel>
                                  <DropdownMenuItem asChild>
                                    <Link to={`/content/${content.id}`} className="cursor-pointer">View</Link>
                                  </DropdownMenuItem>
                                  <DropdownMenuItem asChild>
                                    <Link to={`/content/${content.id}/edit`} className="cursor-pointer">Edit</Link>
                                  </DropdownMenuItem>
                                  {content.status === "draft" && (
                                    <DropdownMenuItem asChild>
                                      <Link to={`/content/${content.id}/schedule`} className="cursor-pointer">Schedule</Link>
                                    </DropdownMenuItem>
                                  )}
                                  <DropdownMenuSeparator />
                                  <DropdownMenuItem className="text-destructive cursor-pointer" onClick={() => handleDeleteClick(content.id)}>
                                    Delete
                                  </DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </TabsContent>
              <TabsContent value="calendar" className="mt-4">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center p-8">
                      <p className="text-muted-foreground">Calendar view will be implemented here.</p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </CardContent>
      </Card>

      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Content</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this content? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
            <Button variant="destructive" onClick={handleDeleteConfirm}>Delete</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
