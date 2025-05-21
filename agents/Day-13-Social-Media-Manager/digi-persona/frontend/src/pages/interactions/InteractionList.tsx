import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import interactionService, { Interaction, InteractionFilter } from "@/api/interactionService";
import { usePersonaStore } from "@/store/personaStore";

// Type for processed interactions
interface ProcessedInteraction {
  id: number;
  type: string;
  platform: string;
  content: string;
  author: {
    name: string;
    username: string;
    avatar: string;
  };
  personaId: number;
  personaName: string;
  personaAvatar: string;
  timestamp: string;
  status: string;
  response: string | null;
}

export function InteractionList() {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [personaFilter, setPersonaFilter] = useState("all");
  const [platformFilter, setPlatformFilter] = useState("all");
  const [selectedInteraction, setSelectedInteraction] = useState<ProcessedInteraction | null>(null);
  const [responseDialogOpen, setResponseDialogOpen] = useState(false);
  const [responseText, setResponseText] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [interactions, setInteractions] = useState<Interaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { personas } = usePersonaStore();
  
  // Fetch interactions
  useEffect(() => {
    const fetchInteractions = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const filter: InteractionFilter = {};
        
        if (personaFilter !== "all") {
          filter.persona_id = parseInt(personaFilter);
        }
        
        if (platformFilter !== "all") {
          filter.platform = platformFilter.toLowerCase();
        }
        
        if (statusFilter !== "all") {
          filter.status = statusFilter;
        }
        
        if (searchQuery) {
          filter.content_contains = searchQuery;
        }
        
        const result = await interactionService.filterInteractions(filter);
        setInteractions(result.items);
      } catch (err) {
        console.error("Error fetching interactions:", err);
        setError("Failed to load interactions. Please try again.");
        toast.error("Failed to load interactions");
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchInteractions();
  }, [personaFilter, platformFilter, statusFilter, searchQuery]);

  // Process interactions for display
  const processedInteractions: ProcessedInteraction[] = interactions.map(interaction => {
    const persona = personas.find(p => p.id === interaction.persona_id);
    return {
      id: interaction.id,
      type: interaction.type,
      platform: interaction.platform.charAt(0).toUpperCase() + interaction.platform.slice(1),
      content: interaction.content,
      author: {
        name: interaction.author.name || interaction.author.screen_name || interaction.author.display_name || "Unknown",
        username: interaction.author.username || interaction.author.handle || `@${interaction.author.screen_name}` || "",
        avatar: interaction.author.profile_image_url || "/avatars/default.png"
      },
      personaId: interaction.persona_id,
      personaName: persona?.name || "Unknown Persona",
      personaAvatar: persona?.avatar_url || "/avatars/default.png",
      timestamp: interaction.created_at,
      status: interaction.status,
      response: interaction.response || null
    };
  });

  const handleRespondClick = (interaction: ProcessedInteraction) => {
    setSelectedInteraction(interaction);
    setResponseText(interaction.response || "");
    setResponseDialogOpen(true);
  };

  const handleGenerateResponse = async () => {
    if (!selectedInteraction) return;
    
    setIsGenerating(true);
    try {
      const response = await interactionService.generateResponse(selectedInteraction.id);
      setResponseText(response.generated_response);
      toast.success("Response generated successfully");
    } catch (error) {
      toast.error("Failed to generate response");
      console.error("Error generating response:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSubmitResponse = async () => {
    if (!selectedInteraction || !responseText.trim()) return;
    
    setIsSubmitting(true);
    try {
      await interactionService.respondToInteraction(selectedInteraction.id, {
        content: responseText
      });
      
      toast.success("Response submitted successfully");
      setResponseDialogOpen(false);
      setSelectedInteraction(null);
      setResponseText("");
      
      // Refresh the interactions list
      const result = await interactionService.filterInteractions({});
      setInteractions(result.items);
    } catch (error) {
      toast.error("Failed to submit response");
      console.error("Error submitting response:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getInteractionTypeIcon = (type: string) => {
    switch (type) {
      case "mention":
        return "@";
      case "reply":
        return "↩️";
      case "direct_message":
        return "✉️";
      case "comment":
        return "💬";
      default:
        return "🔔";
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Interactions</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Interaction Management</CardTitle>
          <CardDescription>Monitor and respond to interactions across all platforms</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <Input
                placeholder="Search interactions..."
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
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="responded">Responded</SelectItem>
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
                    <SelectItem value="twitter">Twitter</SelectItem>
                    <SelectItem value="linkedin">LinkedIn</SelectItem>
                    <SelectItem value="bluesky">Bluesky</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {error && (
              <div className="p-4 mb-4 text-sm text-red-700 bg-red-100 rounded-lg">
                {error}
              </div>
            )}

            <Tabs defaultValue="list" className="mt-6">
              <TabsList>
                <TabsTrigger value="list">List View</TabsTrigger>
                <TabsTrigger value="grid">Grid View</TabsTrigger>
              </TabsList>
              
              <TabsContent value="list" className="mt-4">
                {isLoading ? (
                  <div className="flex justify-center items-center py-12">
                    <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mr-2"></div>
                    <p>Loading interactions...</p>
                  </div>
                ) : processedInteractions.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-muted-foreground">No interactions found. Try adjusting your filters.</p>
                    <Button 
                      onClick={() => interactionService.syncInteractions()} 
                      className="mt-4"
                    >
                      Sync Interactions
                    </Button>
                  </div>
                ) : (
                  <div className="rounded-md border">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Interaction</TableHead>
                          <TableHead>Persona</TableHead>
                          <TableHead>Platform</TableHead>
                          <TableHead>Time</TableHead>
                          <TableHead>Status</TableHead>
                          <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {processedInteractions.map((interaction) => (
                          <TableRow key={interaction.id}>
                            <TableCell>
                              <div className="flex items-start gap-2">
                                <div className="flex-shrink-0 mt-1 text-lg">
                                  {getInteractionTypeIcon(interaction.type)}
                                </div>
                                <div>
                                  <div className="flex items-center gap-2">
                                    <Avatar className="h-6 w-6">
                                      <AvatarImage src={interaction.author.avatar} alt={interaction.author.name} />
                                      <AvatarFallback>{interaction.author.name.substring(0, 2)}</AvatarFallback>
                                    </Avatar>
                                    <span className="font-medium">{interaction.author.name}</span>
                                    <span className="text-sm text-muted-foreground">{interaction.author.username}</span>
                                  </div>
                                  <p className="text-sm mt-1">{interaction.content}</p>
                                  {interaction.response && (
                                    <div className="mt-2 text-sm text-muted-foreground border-l-2 pl-2">
                                      <p>Your response: {interaction.response}</p>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center gap-2">
                                <Avatar className="h-6 w-6">
                                  <AvatarImage src={interaction.personaAvatar} alt={interaction.personaName} />
                                  <AvatarFallback>{interaction.personaName.substring(0, 2)}</AvatarFallback>
                                </Avatar>
                                <span>{interaction.personaName}</span>
                              </div>
                            </TableCell>
                            <TableCell>{interaction.platform}</TableCell>
                            <TableCell>{formatDate(interaction.timestamp)}</TableCell>
                            <TableCell>
                              <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                                interaction.status === "responded" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                              }`}>
                                {interaction.status === "responded" ? "Responded" : "Pending"}
                              </div>
                            </TableCell>
                            <TableCell className="text-right">
                              <Button
                                variant={interaction.status === "responded" ? "outline" : "default"}
                                size="sm"
                                onClick={() => handleRespondClick(interaction)}
                              >
                                {interaction.status === "responded" ? "Edit Response" : "Respond"}
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="grid" className="mt-4">
                {isLoading ? (
                  <div className="flex justify-center items-center py-12">
                    <div className="animate-spin w-6 h-6 border-2 border-primary border-t-transparent rounded-full mr-2"></div>
                    <p>Loading interactions...</p>
                  </div>
                ) : processedInteractions.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-muted-foreground">No interactions found. Try adjusting your filters.</p>
                    <Button 
                      onClick={() => interactionService.syncInteractions()} 
                      className="mt-4"
                    >
                      Sync Interactions
                    </Button>
                  </div>
                ) : (
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    {processedInteractions.map((interaction) => (
                      <Card key={interaction.id}>
                        <CardHeader className="pb-2">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <div className="text-lg">
                                {getInteractionTypeIcon(interaction.type)}
                              </div>
                              <CardTitle className="text-base">{interaction.type.replace("_", " ")}</CardTitle>
                            </div>
                            <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                              interaction.status === "responded" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                            }`}>
                              {interaction.status === "responded" ? "Responded" : "Pending"}
                            </div>
                          </div>
                          <CardDescription className="flex items-center gap-2 mt-2">
                            <Avatar className="h-6 w-6">
                              <AvatarImage src={interaction.author.avatar} alt={interaction.author.name} />
                              <AvatarFallback>{interaction.author.name.substring(0, 2)}</AvatarFallback>
                            </Avatar>
                            {interaction.author.name} ({interaction.author.username})
                          </CardDescription>
                        </CardHeader>
                        <CardContent className="pb-2">
                          <p className="text-sm">{interaction.content}</p>
                          {interaction.response && (
                            <div className="mt-2 text-sm text-muted-foreground border-l-2 pl-2">
                              <p>Your response: {interaction.response}</p>
                            </div>
                          )}
                          <div className="mt-4 flex items-center justify-between text-sm text-muted-foreground">
                            <div className="flex items-center gap-2">
                              <Avatar className="h-5 w-5">
                                <AvatarImage src={interaction.personaAvatar} alt={interaction.personaName} />
                                <AvatarFallback>{interaction.personaName.substring(0, 2)}</AvatarFallback>
                              </Avatar>
                              {interaction.personaName}
                            </div>
                            <div>{interaction.platform}</div>
                          </div>
                        </CardContent>
                        <CardFooter className="pt-2">
                          <Button
                            variant={interaction.status === "responded" ? "outline" : "default"}
                            size="sm"
                            className="w-full"
                            onClick={() => handleRespondClick(interaction)}
                          >
                            {interaction.status === "responded" ? "Edit Response" : "Respond"}
                          </Button>
                        </CardFooter>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </div>
        </CardContent>
      </Card>

      <Dialog open={responseDialogOpen} onOpenChange={setResponseDialogOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Respond to Interaction</DialogTitle>
            <DialogDescription>
              Craft a response as {selectedInteraction?.personaName} on {selectedInteraction?.platform}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="rounded-md border p-4">
              <div className="flex items-center gap-2 mb-2">
                <Avatar className="h-6 w-6">
                  <AvatarImage src={selectedInteraction?.author.avatar} alt={selectedInteraction?.author.name} />
                  <AvatarFallback>{selectedInteraction?.author.name.substring(0, 2)}</AvatarFallback>
                </Avatar>
                <span className="font-medium">{selectedInteraction?.author.name}</span>
                <span className="text-sm text-muted-foreground">{selectedInteraction?.author.username}</span>
              </div>
              <p className="text-sm">{selectedInteraction?.content}</p>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="response" className="text-sm font-medium">
                  Your Response
                </label>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleGenerateResponse}
                  disabled={isGenerating}
                >
                  {isGenerating ? "Generating..." : "Generate AI Response"}
                </Button>
              </div>
              <Textarea
                id="response"
                value={responseText}
                onChange={(e) => setResponseText(e.target.value)}
                placeholder="Write your response..."
                className="min-h-[150px]"
                disabled={isGenerating || isSubmitting}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setResponseDialogOpen(false)} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button onClick={handleSubmitResponse} disabled={isGenerating || isSubmitting || !responseText.trim()}>
              {isSubmitting ? "Submitting..." : "Submit Response"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
