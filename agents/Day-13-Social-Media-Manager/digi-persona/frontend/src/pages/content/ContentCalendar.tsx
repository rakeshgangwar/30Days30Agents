import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, addMonths, subMonths } from "date-fns";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Spinner } from "@/components/ui/spinner";
import { useToast } from "@/components/ui/use-toast";
import { usePersonaStore } from "@/store/personaStore";
import { useContentStore } from "@/store/contentStore";

// Helper function to extract title from content text
const extractTitle = (text: string): string => {
  // Get first sentence or first 50 characters
  const firstSentence = text.split(/[.!?]\s/)[0];
  if (firstSentence.length < 50) return firstSentence;
  return firstSentence.substring(0, 47) + '...';
};


export function ContentCalendar() {
  const [searchParams] = useSearchParams();
  const { personas } = usePersonaStore();
  const { upcomingContent, fetchUpcomingContent, isLoading, error } = useContentStore();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedPersona, setSelectedPersona] = useState<string>("all");
  const [selectedPlatform, setSelectedPlatform] = useState<string>("all");
  const [selectedContent, setSelectedContent] = useState<any>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);

  // Check for personaId in URL parameters when component mounts
  useEffect(() => {
    const personaIdParam = searchParams.get("personaId");
    if (personaIdParam) {
      setSelectedPersona(personaIdParam);
    }
  }, [searchParams]);

  // Get the days for the current month
  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const monthDays = eachDayOfInterval({ start: monthStart, end: monthEnd });

  // Fetch upcoming content when component mounts or filters change
  useEffect(() => {
    const params: any = { hours_ahead: 720 }; // 30 days ahead

    if (selectedPersona !== "all") {
      params.persona_id = parseInt(selectedPersona);
    }

    if (selectedPlatform !== "all") {
      params.platform = selectedPlatform.toLowerCase();
    }

    fetchUpcomingContent(params);
  }, [fetchUpcomingContent, selectedPersona, selectedPlatform]);

  // Show error toast if fetch fails
  const { toast } = useToast();
  useEffect(() => {
    if (error) {
      toast({
        title: "Error",
        description: "Failed to fetch scheduled content. Please try again.",
        variant: "destructive",
      });
    }
  }, [error, toast]);

  // Process content for display
  const processedContent = upcomingContent.map(content => ({
    id: content.id,
    title: extractTitle(content.text),
    text: content.text,
    personaId: content.persona_id,
    personaName: personas.find(p => p.id === content.persona_id)?.name || "Unknown",
    personaAvatar: "/avatars/default.png",
    platform: content.platform.charAt(0).toUpperCase() + content.platform.slice(1),
    contentType: content.content_type.charAt(0).toUpperCase() + content.content_type.slice(1),
    scheduledTime: content.scheduled_time,
  }));

  // Filter content based on selected persona and platform
  const filteredContent = processedContent;

  // Group content by date
  const contentByDate = filteredContent.reduce((acc, content) => {
    const date = new Date(content.scheduledTime || new Date()).toDateString();
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(content);
    return acc;
  }, {} as Record<string, any[]>);

  const handlePreviousMonth = () => {
    setCurrentDate(subMonths(currentDate, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(addMonths(currentDate, 1));
  };

  const handleContentClick = (content: any) => {
    setSelectedContent(content);
    setDetailsDialogOpen(true);
  };

  const getPlatformColor = (platform: string) => {
    switch (platform.toLowerCase()) {
      case "twitter":
        return "bg-blue-100 text-blue-800";
      case "linkedin":
        return "bg-indigo-100 text-indigo-800";
      case "bluesky":
        return "bg-sky-100 text-sky-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Content Calendar</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => window.location.href = "/content/schedule"}>Schedule Content</Button>
          <Button onClick={() => window.location.href = "/content/new"}>Create Content</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <CardTitle>Content Schedule</CardTitle>
              <CardDescription>Plan and manage your scheduled content</CardDescription>
            </div>
            <div className="flex flex-wrap gap-2">
              <Select value={selectedPersona} onValueChange={setSelectedPersona}>
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
              <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
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
        </CardHeader>
        <CardContent>


          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <Spinner className="h-8 w-8" />
              <span className="ml-2">Loading content...</span>
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between mb-4">
                <Button variant="outline" size="sm" onClick={handlePreviousMonth}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
                    <path d="m15 18-6-6 6-6" />
                  </svg>
                  Previous
                </Button>
                <h2 className="text-xl font-bold">{format(currentDate, "MMMM yyyy")}</h2>
                <Button variant="outline" size="sm" onClick={handleNextMonth}>
                  Next
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="ml-1">
                    <path d="m9 18 6-6-6-6" />
                  </svg>
                </Button>
              </div>

              <div className="grid grid-cols-7 gap-px bg-muted rounded-lg overflow-hidden">
                {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
                  <div key={day} className="bg-background p-2 text-center text-sm font-medium">
                    {day}
                  </div>
                ))}

                {Array.from({ length: monthStart.getDay() }).map((_, index) => (
                  <div key={`empty-start-${index}`} className="bg-background p-2 min-h-[120px]" />
                ))}

                {monthDays.map((day) => {
                  const dateString = day.toDateString();
                  const dayContent = contentByDate[dateString] || [];
                  const isCurrentMonth = isSameMonth(day, currentDate);
                  const isCurrentDay = isToday(day);

                  return (
                    <div
                      key={day.toString()}
                      className={`bg-background p-2 min-h-[120px] ${
                        !isCurrentMonth ? "opacity-50" : ""
                      } ${isCurrentDay ? "ring-2 ring-primary ring-inset" : ""}`}
                    >
                      <div className="text-right text-sm font-medium mb-1">
                        {format(day, "d")}
                      </div>
                      <div className="space-y-1">
                        {dayContent.slice(0, 3).map((content) => (
                          <div
                            key={content.id}
                            className="text-xs p-1 rounded cursor-pointer hover:bg-muted"
                            onClick={() => handleContentClick(content)}
                          >
                            <div className="flex items-center gap-1">
                              <Avatar className="h-4 w-4">
                                <AvatarImage src={content.personaAvatar} alt={content.personaName} />
                                <AvatarFallback>{content.personaName.substring(0, 2)}</AvatarFallback>
                              </Avatar>
                              <span className={`px-1 rounded text-[10px] ${getPlatformColor(content.platform)}`}>
                                {content.platform}
                              </span>
                            </div>
                            <div className="truncate font-medium mt-1">{content.title}</div>
                          </div>
                        ))}
                        {dayContent.length > 3 && (
                          <div className="text-xs text-muted-foreground text-center">
                            +{dayContent.length - 3} more
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}

                {Array.from({ length: 6 - monthEnd.getDay() }).map((_, index) => (
                  <div key={`empty-end-${index}`} className="bg-background p-2 min-h-[120px]" />
                ))}
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <Dialog open={detailsDialogOpen} onOpenChange={setDetailsDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          {selectedContent && (
            <>
              <DialogHeader>
                <DialogTitle>{selectedContent.title}</DialogTitle>
                <DialogDescription>
                  Scheduled for {format(new Date(selectedContent.scheduledTime), "PPP 'at' p")}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="flex items-center gap-2">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={selectedContent.personaAvatar} alt={selectedContent.personaName} />
                    <AvatarFallback>{selectedContent.personaName.substring(0, 2)}</AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="font-medium">{selectedContent.personaName}</div>
                    <div className="text-sm text-muted-foreground">{selectedContent.contentType} on {selectedContent.platform}</div>
                  </div>
                </div>
                <div className="rounded-md border p-4">
                  <p className="whitespace-pre-line">{selectedContent.text}</p>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setDetailsDialogOpen(false)}>Close</Button>
                <Button variant="outline" onClick={() => window.location.href = `/content/${selectedContent.id}/edit`}>Edit</Button>
                <Button>Reschedule</Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
