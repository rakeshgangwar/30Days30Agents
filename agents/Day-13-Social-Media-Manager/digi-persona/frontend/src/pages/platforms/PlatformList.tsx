import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { usePersonaStore } from "@/store/personaStore";
import platformService, { PlatformConnection } from "@/api/platformService";

export function PlatformList() {
  const navigate = useNavigate();
  const { activePersona } = usePersonaStore();
  const [activeTab, setActiveTab] = useState("all");
  const [disconnectDialogOpen, setDisconnectDialogOpen] = useState(false);
  const [platformToDisconnect, setPlatformToDisconnect] = useState<number | null>(null);
  const [platforms, setPlatforms] = useState<PlatformConnection[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSyncing, setIsSyncing] = useState<number | null>(null);

  useEffect(() => {
    fetchPlatforms();
  }, [activePersona]);

  const fetchPlatforms = async () => {
    setIsLoading(true);
    try {
      const response = await platformService.getPlatformConnections({ active_only: true });
      setPlatforms(response.items);
    } catch (error) {
      console.error("Error fetching platforms:", error);
      toast.error("Failed to fetch platform connections");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisconnectClick = (platformId: number) => {
    setPlatformToDisconnect(platformId);
    setDisconnectDialogOpen(true);
  };

  const handleDisconnectConfirm = async () => {
    if (platformToDisconnect === null) return;
    
    try {
      await platformService.disconnectPlatform(platformToDisconnect);
      toast.success("Platform disconnected successfully");
      fetchPlatforms(); // Refresh the list
    } catch (error) {
      console.error("Error disconnecting platform:", error);
      toast.error("Failed to disconnect platform");
    } finally {
      setDisconnectDialogOpen(false);
      setPlatformToDisconnect(null);
    }
  };

  const handleSyncPlatform = async (platformId: number) => {
    setIsSyncing(platformId);
    try {
      await platformService.syncPlatform(platformId);
      // Refresh platform data
      const updatedPlatform = await platformService.getPlatformConnection(platformId);
      setPlatforms(prevPlatforms => 
        prevPlatforms.map(p => p.id === platformId ? updatedPlatform : p)
      );
      toast.success("Platform data synced successfully");
    } catch (error) {
      console.error("Error syncing platform:", error);
      toast.error("Failed to sync platform data");
    } finally {
      setIsSyncing(null);
    }
  };

  const filteredPlatforms = activeTab === "all"
    ? platforms
    : platforms.filter(p => p.platform_name.toLowerCase() === activeTab.toLowerCase());

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case "twitter":
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z" />
          </svg>
        );
      case "linkedin":
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z" />
            <rect width="4" height="12" x="2" y="9" />
            <circle cx="4" cy="4" r="2" />
          </svg>
        );
      case "bluesky":
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
          </svg>
        );
      default:
        return (
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="2" x2="22" y1="12" y2="12" />
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
          </svg>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Platform Connections</h1>
        <Button onClick={() => navigate("/platforms/connect")}>Connect Platform</Button>
      </div>

      <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4">
          <TabsTrigger value="all">All Platforms</TabsTrigger>
          <TabsTrigger value="twitter">Twitter</TabsTrigger>
          <TabsTrigger value="linkedin">LinkedIn</TabsTrigger>
          <TabsTrigger value="bluesky">Bluesky</TabsTrigger>
        </TabsList>
        
        {isLoading ? (
          <div className="flex justify-center p-8">
            <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full"></div>
          </div>
        ) : filteredPlatforms.length === 0 ? (
          <div className="text-center p-8">
            <p className="text-muted-foreground">No platform connections found.</p>
            <Button className="mt-4" onClick={() => navigate("/platforms/connect")}>Connect a Platform</Button>
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredPlatforms.map((platform) => (
              <Card key={platform.id}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-2 rounded-full bg-primary/10">
                        {getPlatformIcon(platform.platform_name)}
                      </div>
                      <CardTitle>{platform.platform_name}</CardTitle>
                    </div>
                    <div className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-green-100 text-green-800`}>
                      Connected
                    </div>
                  </div>
                  <CardDescription className="flex items-center gap-2 mt-2">
                    <Avatar className="h-6 w-6">
                      <AvatarImage src={`/avatars/${platform.platform_name.toLowerCase()}.png`} alt={platform.platform_name} />
                      <AvatarFallback>{platform.platform_name.substring(0, 2).toUpperCase()}</AvatarFallback>
                    </Avatar>
                    {platform.username}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pb-2">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Platform ID:</span>
                      <span className="font-medium">{platform.platform_id}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Last Updated:</span>
                      <span>{formatDate(platform.updated_at)}</span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 mt-4 text-center">
                      <div className="space-y-1">
                        <p className="text-xl font-bold">{platform.metrics.follower_count}</p>
                        <p className="text-xs text-muted-foreground">Followers</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-xl font-bold">{platform.metrics.following_count}</p>
                        <p className="text-xs text-muted-foreground">Following</p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-xl font-bold">{platform.metrics.post_count}</p>
                        <p className="text-xs text-muted-foreground">Posts</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="flex justify-between">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleSyncPlatform(platform.id)}
                    disabled={isSyncing === platform.id}
                  >
                    {isSyncing === platform.id ? "Syncing..." : "Sync Now"}
                  </Button>
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
                      <DropdownMenuItem className="cursor-pointer" onClick={() => handleSyncPlatform(platform.id)}>
                        Sync Data
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem className="text-destructive cursor-pointer" onClick={() => handleDisconnectClick(platform.id)}>
                        Disconnect
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </Tabs>

      <Dialog open={disconnectDialogOpen} onOpenChange={setDisconnectDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Disconnect Platform</DialogTitle>
            <DialogDescription>
              Are you sure you want to disconnect this platform? Your persona will no longer be able to post or interact on this platform.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDisconnectDialogOpen(false)}>Cancel</Button>
            <Button variant="destructive" onClick={handleDisconnectConfirm}>Disconnect</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
