import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { usePersonaStore } from "@/store/personaStore";

export function Dashboard() {
  const [contentFilter, setContentFilter] = useState("all");
  const [interactionFilter, setInteractionFilter] = useState("all");
  const [analyticsTimeframe, setAnalyticsTimeframe] = useState("7days");
  const { personas } = usePersonaStore();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="flex items-center gap-2">
          <Button asChild>
            <Link to="/content/new">Create Content</Link>
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="interactions">Interactions</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Content</CardTitle>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-muted-foreground">
                  <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">24</div>
                <p className="text-xs text-muted-foreground">+12% from last month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Interactions</CardTitle>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-muted-foreground">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">142</div>
                <p className="text-xs text-muted-foreground">+28% from last month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Platforms</CardTitle>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-muted-foreground">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
                </svg>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3</div>
                <p className="text-xs text-muted-foreground">Twitter, LinkedIn, Bluesky</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Personas</CardTitle>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-muted-foreground">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3</div>
                <p className="text-xs text-muted-foreground">Active personas</p>
              </CardContent>
            </Card>
          </div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
            <Card className="col-span-4">
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Your recent content and interactions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center gap-4 rounded-lg border p-3">
                    <div className="flex-1">
                      <h3 className="font-medium">New tweet published</h3>
                      <p className="text-sm text-muted-foreground">Tech Expert persona on Twitter</p>
                    </div>
                    <div className="text-sm text-muted-foreground">2h ago</div>
                  </div>
                  <div className="flex items-center gap-4 rounded-lg border p-3">
                    <div className="flex-1">
                      <h3 className="font-medium">New comment received</h3>
                      <p className="text-sm text-muted-foreground">Finance Guru persona on LinkedIn</p>
                    </div>
                    <div className="text-sm text-muted-foreground">5h ago</div>
                  </div>
                  <div className="flex items-center gap-4 rounded-lg border p-3">
                    <div className="flex-1">
                      <h3 className="font-medium">Content scheduled</h3>
                      <p className="text-sm text-muted-foreground">Health Coach persona on Bluesky</p>
                    </div>
                    <div className="text-sm text-muted-foreground">Yesterday</div>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="col-span-3">
              <CardHeader>
                <CardTitle>Upcoming Content</CardTitle>
                <CardDescription>Scheduled for the next 24 hours</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center gap-4 rounded-lg border p-3">
                    <div className="flex-1">
                      <h3 className="font-medium">AI trends in 2024</h3>
                      <p className="text-sm text-muted-foreground">Tech Expert • Twitter • Today 4:00 PM</p>
                    </div>
                    <Button variant="outline" size="sm">Edit</Button>
                  </div>
                  <div className="flex items-center gap-4 rounded-lg border p-3">
                    <div className="flex-1">
                      <h3 className="font-medium">Investment strategies</h3>
                      <p className="text-sm text-muted-foreground">Finance Guru • LinkedIn • Tomorrow 9:00 AM</p>
                    </div>
                    <Button variant="outline" size="sm">Edit</Button>
                  </div>
                  <div className="flex items-center gap-4 rounded-lg border p-3">
                    <div className="flex-1">
                      <h3 className="font-medium">Wellness tips</h3>
                      <p className="text-sm text-muted-foreground">Health Coach • Bluesky • Tomorrow 2:00 PM</p>
                    </div>
                    <Button variant="outline" size="sm">Edit</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        <TabsContent value="content" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Select value={contentFilter} onValueChange={setContentFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Content</SelectItem>
                  <SelectItem value="published">Published</SelectItem>
                  <SelectItem value="scheduled">Scheduled</SelectItem>
                  <SelectItem value="draft">Drafts</SelectItem>
                </SelectContent>
              </Select>
              <Input placeholder="Search content..." className="w-[250px]" />
            </div>
            <Button asChild>
              <Link to="/content/new">Create New</Link>
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* Published Content Card */}
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">AI trends in 2024</CardTitle>
                  <Badge>Published</Badge>
                </div>
                <CardDescription className="flex items-center gap-2">
                  <Avatar className="h-5 w-5">
                    <AvatarImage src="/avatars/tech.png" alt="Tech Expert" />
                    <AvatarFallback>TE</AvatarFallback>
                  </Avatar>
                  Tech Expert • Twitter
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="line-clamp-3 text-sm text-muted-foreground">
                  Exploring the latest AI trends that are shaping the technology landscape in 2024. From generative AI to autonomous systems, these innovations are transforming industries.
                </p>
              </CardContent>
              <CardFooter className="flex justify-between">
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M7 10v12" />
                      <path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2h0a3.13 3.13 0 0 1 3 3.88Z" />
                    </svg>
                    <span>24</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                    </svg>
                    <span>8</span>
                  </div>
                </div>
                <div className="text-sm text-muted-foreground">2 hours ago</div>
              </CardFooter>
            </Card>

            {/* Scheduled Content Card */}
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Investment strategies</CardTitle>
                  <Badge variant="outline">Scheduled</Badge>
                </div>
                <CardDescription className="flex items-center gap-2">
                  <Avatar className="h-5 w-5">
                    <AvatarImage src="/avatars/finance.png" alt="Finance Guru" />
                    <AvatarFallback>FG</AvatarFallback>
                  </Avatar>
                  Finance Guru • LinkedIn
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="line-clamp-3 text-sm text-muted-foreground">
                  Diversification is key to managing risk in your investment portfolio. This post explores various strategies for balancing growth and security in today's market conditions.
                </p>
              </CardContent>
              <CardFooter className="flex justify-between">
                <div className="text-sm text-muted-foreground">
                  Scheduled for tomorrow, 9:00 AM
                </div>
                <Button variant="outline" size="sm">Edit</Button>
              </CardFooter>
            </Card>

            {/* Draft Content Card */}
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">Wellness routine</CardTitle>
                  <Badge variant="secondary">Draft</Badge>
                </div>
                <CardDescription className="flex items-center gap-2">
                  <Avatar className="h-5 w-5">
                    <AvatarImage src="/avatars/health.png" alt="Health Coach" />
                    <AvatarFallback>HC</AvatarFallback>
                  </Avatar>
                  Health Coach • Bluesky
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="line-clamp-3 text-sm text-muted-foreground">
                  Morning routines that boost your energy and set you up for a productive day. Includes meditation, exercise, and nutrition tips for optimal wellness.
                </p>
              </CardContent>
              <CardFooter className="flex justify-end gap-2">
                <Button variant="outline" size="sm">Edit</Button>
                <Button size="sm">Publish</Button>
              </CardFooter>
            </Card>
          </div>

          <div className="flex justify-center">
            <Button variant="outline" asChild>
              <Link to="/content">View All Content</Link>
            </Button>
          </div>
        </TabsContent>
        <TabsContent value="interactions" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Select value={interactionFilter} onValueChange={setInteractionFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Interactions</SelectItem>
                  <SelectItem value="comments">Comments</SelectItem>
                  <SelectItem value="likes">Likes</SelectItem>
                  <SelectItem value="shares">Shares</SelectItem>
                  <SelectItem value="mentions">Mentions</SelectItem>
                </SelectContent>
              </Select>
              <Input placeholder="Search interactions..." className="w-[250px]" />
            </div>
            <Button variant="outline" asChild>
              <Link to="/interactions">View All</Link>
            </Button>
          </div>

          <div className="space-y-4">
            {/* Comment Interaction */}
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Avatar>
                      <AvatarImage src="/avatars/user1.png" alt="User" />
                      <AvatarFallback>JD</AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-medium">John Davis</h3>
                      <p className="text-sm text-muted-foreground">@johndavis</p>
                    </div>
                  </div>
                  <Badge>Comment</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm">Great insights on AI trends! I especially agree with your points about generative AI applications in healthcare.</p>
                <div className="mt-2 text-sm text-muted-foreground">
                  On your post: <span className="font-medium">AI trends in 2024</span>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <div className="text-sm text-muted-foreground">2 hours ago</div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">Like</Button>
                  <Button size="sm">Reply</Button>
                </div>
              </CardFooter>
            </Card>

            {/* Like Interaction */}
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Avatar>
                      <AvatarImage src="/avatars/user2.png" alt="User" />
                      <AvatarFallback>SM</AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-medium">Sarah Miller</h3>
                      <p className="text-sm text-muted-foreground">@sarahmiller</p>
                    </div>
                  </div>
                  <Badge variant="outline">Like</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground">
                  Liked your post: <span className="font-medium">Investment strategies</span>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <div className="text-sm text-muted-foreground">5 hours ago</div>
                <Button variant="outline" size="sm">View Profile</Button>
              </CardFooter>
            </Card>

            {/* Share Interaction */}
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Avatar>
                      <AvatarImage src="/avatars/user3.png" alt="User" />
                      <AvatarFallback>RJ</AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-medium">Robert Johnson</h3>
                      <p className="text-sm text-muted-foreground">@robertj</p>
                    </div>
                  </div>
                  <Badge variant="secondary">Share</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm">Everyone should read this! @sarahmiller @michaelw</p>
                <div className="mt-2 text-sm text-muted-foreground">
                  Shared your post: <span className="font-medium">Wellness tips for busy professionals</span>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <div className="text-sm text-muted-foreground">Yesterday</div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">Like</Button>
                  <Button size="sm">Reply</Button>
                </div>
              </CardFooter>
            </Card>
          </div>
        </TabsContent>
        <TabsContent value="analytics" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Select value={analyticsTimeframe} onValueChange={setAnalyticsTimeframe}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Select timeframe" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7days">Last 7 days</SelectItem>
                  <SelectItem value="30days">Last 30 days</SelectItem>
                  <SelectItem value="90days">Last 90 days</SelectItem>
                  <SelectItem value="year">Last year</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button variant="outline" asChild>
              <Link to="/analytics/reports">Generate Report</Link>
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Total Impressions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">24.5K</div>
                <div className="flex items-center text-xs text-green-500">
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
                    <path d="m6 9 6-6 6 6"/>
                    <path d="M6 12h12"/>
                    <path d="m6 15 6 6 6-6"/>
                  </svg>
                  <span>+18% from previous period</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Engagement Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3.2%</div>
                <div className="flex items-center text-xs text-green-500">
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
                    <path d="m6 9 6-6 6 6"/>
                    <path d="M6 12h12"/>
                    <path d="m6 15 6 6 6-6"/>
                  </svg>
                  <span>+0.8% from previous period</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">New Followers</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">342</div>
                <div className="flex items-center text-xs text-green-500">
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
                    <path d="m6 9 6-6 6 6"/>
                    <path d="M6 12h12"/>
                    <path d="m6 15 6 6 6-6"/>
                  </svg>
                  <span>+24% from previous period</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Click-through Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">1.8%</div>
                <div className="flex items-center text-xs text-red-500">
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
                    <path d="m6 9 6-6 6 6"/>
                    <path d="M6 12h12"/>
                    <path d="m6 15 6 6 6-6"/>
                  </svg>
                  <span>-0.3% from previous period</span>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Platform Performance</CardTitle>
                <CardDescription>Engagement by platform</CardDescription>
              </CardHeader>
              <CardContent className="h-80">
                <div className="flex h-full items-center justify-center">
                  <div className="text-center text-muted-foreground">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mx-auto mb-2 text-primary/50">
                      <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
                      <line x1="3" x2="21" y1="9" y2="9" />
                      <line x1="9" x2="9" y1="21" y2="9" />
                    </svg>
                    <p>Bar chart showing engagement metrics by platform</p>
                    <p className="text-sm">(Twitter, LinkedIn, Bluesky)</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Content Performance</CardTitle>
                <CardDescription>Top performing content</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <h3 className="font-medium">AI trends in 2024</h3>
                      <p className="text-sm text-muted-foreground">Tech Expert • Twitter</p>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">4.8%</div>
                      <p className="text-sm text-muted-foreground">Engagement</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <h3 className="font-medium">Investment strategies</h3>
                      <p className="text-sm text-muted-foreground">Finance Guru • LinkedIn</p>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">3.2%</div>
                      <p className="text-sm text-muted-foreground">Engagement</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <h3 className="font-medium">Wellness tips</h3>
                      <p className="text-sm text-muted-foreground">Health Coach • Bluesky</p>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">2.9%</div>
                      <p className="text-sm text-muted-foreground">Engagement</p>
                    </div>
                  </div>
                </div>
              </CardContent>
              <CardFooter>
                <Button variant="outline" className="w-full" asChild>
                  <Link to="/analytics">View Detailed Analytics</Link>
                </Button>
              </CardFooter>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
