import { useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/use-toast";
import { usePersonaStore } from "@/store/personaStore";
import { useAnalyticsStore, TimeRange } from "@/store/analyticsStore";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

// Colors for charts
const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884d8", "#82ca9d", "#ffc658"];

export function AnalyticsDashboard() {
  const { personas } = usePersonaStore();
  const {
    data,
    isLoading,
    error,
    isRealtime,
    timeRange,
    fetchAnalytics,
    startRealtimeUpdates,
    stopRealtimeUpdates,
    setTimeRange,
    setSelectedPersonaId,
    setSelectedPlatform
  } = useAnalyticsStore();
  const { toast } = useToast();

  // Format date for charts
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  };

  // Fetch analytics data on component mount
  useEffect(() => {
    fetchAnalytics();
    
    // Clean up any WebSocket connection when component unmounts
    return () => {
      stopRealtimeUpdates();
    };
  }, [fetchAnalytics, stopRealtimeUpdates]);

  // Handle time range change
  const handleTimeRangeChange = (value: string) => {
    setTimeRange(value as TimeRange);
    fetchAnalytics({ time_range: value as TimeRange });
  };

  // Handle persona selection change
  const handlePersonaChange = (value: string) => {
    const personaId = value === "all" ? undefined : Number(value);
    setSelectedPersonaId(personaId || null);
    fetchAnalytics({ persona_id: personaId });
  };

  // Handle platform selection change
  const handlePlatformChange = (value: string) => {
    const platform = value === "all" ? undefined : value;
    setSelectedPlatform(platform || null);
    fetchAnalytics({ platform });
  };

  // Toggle real-time updates
  const toggleRealtime = (checked: boolean) => {
    if (checked) {
      startRealtimeUpdates();
      toast({
        title: "Real-time updates enabled",
        description: "Analytics data will update automatically",
      });
    } else {
      stopRealtimeUpdates();
      toast({
        title: "Real-time updates disabled",
        description: "Analytics data will update on demand",
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Analytics</h1>
        <div className="flex items-center gap-2">
          <Select value={timeRange} onValueChange={handleTimeRangeChange}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="Time Range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1w">Last Week</SelectItem>
              <SelectItem value="2w">Last 2 Weeks</SelectItem>
              <SelectItem value="1m">Last Month</SelectItem>
              <SelectItem value="3m">Last 3 Months</SelectItem>
            </SelectContent>
          </Select>
          <Select defaultValue="all" onValueChange={handlePersonaChange}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select Persona" />
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
          <Select defaultValue="all" onValueChange={handlePlatformChange}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select Platform" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Platforms</SelectItem>
              <SelectItem value="twitter">Twitter</SelectItem>
              <SelectItem value="linkedin">LinkedIn</SelectItem>
              <SelectItem value="bluesky">Bluesky</SelectItem>
            </SelectContent>
          </Select>
          <div className="flex items-center space-x-2">
            <Switch id="realtime" checked={isRealtime} onCheckedChange={toggleRealtime} />
            <Label htmlFor="realtime">Real-time</Label>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-destructive/15 p-4 rounded-md text-destructive">
          <p>{error}</p>
          <button 
            className="text-sm underline mt-2" 
            onClick={() => fetchAnalytics()}
          >
            Try again
          </button>
        </div>
      )}

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="engagement">Engagement</TabsTrigger>
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="platforms">Platforms</TabsTrigger>
          <TabsTrigger value="personas">Personas</TabsTrigger>
        </TabsList>
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Engagement Over Time</CardTitle>
              <CardDescription>Daily engagement across all platforms</CardDescription>
            </CardHeader>
            <CardContent className="h-[300px]">
              {isLoading ? (
                <div className="h-full flex items-center justify-center">
                  <Skeleton className="h-[250px] w-full" />
                </div>
              ) : data?.engagement && data.engagement.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={data.engagement}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" tickFormatter={formatDate} />
                    <YAxis />
                    <Tooltip labelFormatter={(label) => formatDate(label as string)} />
                    <Legend />
                    <Line type="monotone" dataKey="twitter" stroke="#1DA1F2" activeDot={{ r: 8 }} />
                    <Line type="monotone" dataKey="linkedin" stroke="#0A66C2" />
                    <Line type="monotone" dataKey="bluesky" stroke="#0560FF" />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <p className="text-muted-foreground">No engagement data available</p>
                </div>
              )}
            </CardContent>
          </Card>
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Content by Type</CardTitle>
                <CardDescription>Distribution of content types</CardDescription>
              </CardHeader>
              <CardContent className="h-[300px]">
                {isLoading ? (
                  <div className="h-full flex items-center justify-center">
                    <Skeleton className="h-[250px] w-full" />
                  </div>
                ) : data?.content_types && data.content_types.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={data.content_types}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {data.content_types.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center">
                    <p className="text-muted-foreground">No content type data available</p>
                  </div>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Interaction Types</CardTitle>
                <CardDescription>Breakdown of interaction types</CardDescription>
              </CardHeader>
              <CardContent className="h-[300px]">
                {isLoading ? (
                  <div className="h-full flex items-center justify-center">
                    <Skeleton className="h-[250px] w-full" />
                  </div>
                ) : data?.interaction_types && data.interaction_types.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={data.interaction_types}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {data.interaction_types.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-full flex items-center justify-center">
                    <p className="text-muted-foreground">No interaction type data available</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        <TabsContent value="engagement" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Engagement Metrics</CardTitle>
              <CardDescription>Detailed engagement analysis</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-2">
                  <Skeleton className="h-[20px] w-full" />
                  <Skeleton className="h-[20px] w-full" />
                  <Skeleton className="h-[20px] w-full" />
                </div>
              ) : data?.engagement && data.engagement.length > 0 ? (
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={data.engagement}
                      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tickFormatter={formatDate} />
                      <YAxis />
                      <Tooltip labelFormatter={(label) => formatDate(label as string)} />
                      <Legend />
                      <Line type="monotone" dataKey="twitter" stroke="#1DA1F2" activeDot={{ r: 8 }} />
                      <Line type="monotone" dataKey="linkedin" stroke="#0A66C2" />
                      <Line type="monotone" dataKey="bluesky" stroke="#0560FF" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <p className="text-muted-foreground">No engagement data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="content" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Content Performance</CardTitle>
              <CardDescription>Analysis of content performance</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-2">
                  <Skeleton className="h-[20px] w-full" />
                  <Skeleton className="h-[20px] w-full" />
                  <Skeleton className="h-[20px] w-full" />
                </div>
              ) : data?.content_types && data.content_types.length > 0 ? (
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={data.content_types}
                      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="value" fill="#8884d8" name="Count" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <p className="text-muted-foreground">No content performance data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="platforms" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Platform Comparison</CardTitle>
              <CardDescription>Performance across different platforms</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px]">
              {isLoading ? (
                <div className="h-full flex items-center justify-center">
                  <Skeleton className="h-[350px] w-full" />
                </div>
              ) : data?.platforms && data.platforms.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={data.platforms}
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="followers" fill="#8884d8" name="Followers" />
                    <Bar dataKey="engagement" fill="#82ca9d" name="Engagement" />
                    <Bar dataKey="posts" fill="#ffc658" name="Posts" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <p className="text-muted-foreground">No platform data available</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="personas" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Persona Performance</CardTitle>
              <CardDescription>Comparative performance of personas</CardDescription>
            </CardHeader>
            <CardContent className="h-[400px]">
              {isLoading ? (
                <div className="h-full flex items-center justify-center">
                  <Skeleton className="h-[350px] w-full" />
                </div>
              ) : data?.personas && data.personas.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={data.personas}
                    margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="followers" fill="#8884d8" name="Followers" />
                    <Bar dataKey="engagement" fill="#82ca9d" name="Engagement" />
                    <Bar dataKey="posts" fill="#ffc658" name="Posts" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <p className="text-muted-foreground">No persona performance data available</p>
                </div>
              )}
            </CardContent>
          </Card>
          <div className="grid gap-4 md:grid-cols-3">
            {data?.personas && data.personas.map((persona) => (
              <Card key={persona.id}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <div className="flex items-center space-x-2">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src={persona.avatar} alt={persona.name} />
                      <AvatarFallback>{persona.name.substring(0, 2)}</AvatarFallback>
                    </Avatar>
                    <CardTitle className="text-sm font-medium">{persona.name}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="flex flex-col">
                      <span className="text-muted-foreground">Posts</span>
                      <span className="text-xl font-bold">{persona.posts}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-muted-foreground">Engagement</span>
                      <span className="text-xl font-bold">{persona.engagement}</span>
                    </div>
                    <div className="flex flex-col">
                      <span className="text-muted-foreground">Followers</span>
                      <span className="text-xl font-bold">{persona.followers}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
