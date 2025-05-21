import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { toast } from "sonner";

export function Settings() {
  const [activeTab, setActiveTab] = useState("account");
  const [isSaving, setIsSaving] = useState(false);
  
  // Mock user data
  const [userData, setUserData] = useState({
    name: "John Doe",
    email: "john.doe@example.com",
    avatar: "/avatars/user.png",
    timezone: "America/New_York",
    language: "en",
    theme: "system",
    notifications: {
      email: true,
      browser: true,
      contentScheduled: true,
      contentPublished: true,
      interactions: true,
      reports: false
    },
    apiKey: "sk_test_1234567890abcdef",
    twoFactorEnabled: false
  });

  // Mock API settings
  const [apiSettings, setApiSettings] = useState({
    openaiApiKey: "sk_openai_1234567890abcdef",
    openaiModel: "gpt-4o",
    maxTokens: 2048,
    temperature: 0.7,
    contentGeneration: {
      maxRetries: 3,
      includeHashtags: true,
      autoSchedule: false
    }
  });

  // Mock platform settings
  const [platformSettings, setplatformSettings] = useState({
    defaultPlatforms: ["twitter", "linkedin"],
    autoPublish: false,
    requireApproval: true,
    maxScheduledPerDay: 5,
    blacklistedWords: "spam, inappropriate, offensive",
    contentFilters: {
      profanityFilter: true,
      sentimentAnalysis: true,
      brandSafetyCheck: false
    }
  });

  const handleSaveAccount = () => {
    setIsSaving(true);
    // Simulate API call
    setTimeout(() => {
      toast.success("Account settings saved successfully");
      setIsSaving(false);
    }, 1000);
  };

  const handleSaveNotifications = () => {
    setIsSaving(true);
    // Simulate API call
    setTimeout(() => {
      toast.success("Notification preferences saved successfully");
      setIsSaving(false);
    }, 1000);
  };

  const handleSaveAPI = () => {
    setIsSaving(true);
    // Simulate API call
    setTimeout(() => {
      toast.success("API settings saved successfully");
      setIsSaving(false);
    }, 1000);
  };

  const handleSavePlatforms = () => {
    setIsSaving(true);
    // Simulate API call
    setTimeout(() => {
      toast.success("Platform settings saved successfully");
      setIsSaving(false);
    }, 1000);
  };

  const handleResetAPIKey = () => {
    // Simulate API call
    setTimeout(() => {
      setUserData({
        ...userData,
        apiKey: "sk_test_" + Math.random().toString(36).substring(2, 15)
      });
      toast.success("API key reset successfully");
    }, 1000);
  };

  const handleToggle2FA = () => {
    setUserData({
      ...userData,
      twoFactorEnabled: !userData.twoFactorEnabled
    });
    toast.success(userData.twoFactorEnabled ? "Two-factor authentication disabled" : "Two-factor authentication enabled");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Settings</h1>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid grid-cols-4 w-full md:w-auto">
          <TabsTrigger value="account">Account</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="api">API</TabsTrigger>
          <TabsTrigger value="platforms">Platforms</TabsTrigger>
        </TabsList>

        <TabsContent value="account" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
              <CardDescription>Update your account settings and preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-4 mb-6">
                <Avatar className="h-20 w-20">
                  <AvatarImage src={userData.avatar} alt={userData.name} />
                  <AvatarFallback>{userData.name.substring(0, 2)}</AvatarFallback>
                </Avatar>
                <div>
                  <Button variant="outline" size="sm">Change Avatar</Button>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={userData.name}
                    onChange={(e) => setUserData({ ...userData, name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={userData.email}
                    onChange={(e) => setUserData({ ...userData, email: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="timezone">Timezone</Label>
                  <Select
                    value={userData.timezone}
                    onValueChange={(value) => setUserData({ ...userData, timezone: value })}
                  >
                    <SelectTrigger id="timezone">
                      <SelectValue placeholder="Select timezone" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="America/New_York">Eastern Time (ET)</SelectItem>
                      <SelectItem value="America/Chicago">Central Time (CT)</SelectItem>
                      <SelectItem value="America/Denver">Mountain Time (MT)</SelectItem>
                      <SelectItem value="America/Los_Angeles">Pacific Time (PT)</SelectItem>
                      <SelectItem value="Europe/London">Greenwich Mean Time (GMT)</SelectItem>
                      <SelectItem value="Europe/Paris">Central European Time (CET)</SelectItem>
                      <SelectItem value="Asia/Tokyo">Japan Standard Time (JST)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="language">Language</Label>
                  <Select
                    value={userData.language}
                    onValueChange={(value) => setUserData({ ...userData, language: value })}
                  >
                    <SelectTrigger id="language">
                      <SelectValue placeholder="Select language" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="es">Spanish</SelectItem>
                      <SelectItem value="fr">French</SelectItem>
                      <SelectItem value="de">German</SelectItem>
                      <SelectItem value="ja">Japanese</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="theme">Theme</Label>
                <Select
                  value={userData.theme}
                  onValueChange={(value) => setUserData({ ...userData, theme: value })}
                >
                  <SelectTrigger id="theme">
                    <SelectValue placeholder="Select theme" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">Light</SelectItem>
                    <SelectItem value="dark">Dark</SelectItem>
                    <SelectItem value="system">System</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end">
              <Button onClick={handleSaveAccount} disabled={isSaving}>
                {isSaving ? "Saving..." : "Save Changes"}
              </Button>
            </CardFooter>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Security</CardTitle>
              <CardDescription>Manage your account security settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">API Key</h3>
                    <p className="text-sm text-muted-foreground">Your API key for accessing the Digi-Persona API</p>
                  </div>
                  <Button variant="outline" onClick={handleResetAPIKey}>Reset API Key</Button>
                </div>
                <div className="flex items-center space-x-2">
                  <Input
                    value={userData.apiKey}
                    readOnly
                    type="password"
                  />
                  <Button variant="ghost" size="icon" onClick={() => {
                    navigator.clipboard.writeText(userData.apiKey);
                    toast.success("API key copied to clipboard");
                  }}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect width="14" height="14" x="8" y="8" rx="2" ry="2" />
                      <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
                    </svg>
                    <span className="sr-only">Copy</span>
                  </Button>
                </div>
              </div>

              <div className="flex items-center justify-between rounded-lg border p-4">
                <div>
                  <h3 className="font-medium">Two-Factor Authentication</h3>
                  <p className="text-sm text-muted-foreground">Add an extra layer of security to your account</p>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={userData.twoFactorEnabled}
                    onCheckedChange={handleToggle2FA}
                  />
                  <span>{userData.twoFactorEnabled ? "Enabled" : "Disabled"}</span>
                </div>
              </div>

              <div className="pt-4">
                <Button variant="outline" className="w-full">Change Password</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Notification Preferences</CardTitle>
              <CardDescription>Manage how you receive notifications</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="font-medium">Notification Channels</h3>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <h4 className="font-medium">Email Notifications</h4>
                    <p className="text-sm text-muted-foreground">Receive notifications via email</p>
                  </div>
                  <Switch
                    checked={userData.notifications.email}
                    onCheckedChange={(checked) => setUserData({
                      ...userData,
                      notifications: { ...userData.notifications, email: checked }
                    })}
                  />
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <h4 className="font-medium">Browser Notifications</h4>
                    <p className="text-sm text-muted-foreground">Receive notifications in your browser</p>
                  </div>
                  <Switch
                    checked={userData.notifications.browser}
                    onCheckedChange={(checked) => setUserData({
                      ...userData,
                      notifications: { ...userData.notifications, browser: checked }
                    })}
                  />
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-medium">Notification Types</h3>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <h4 className="font-medium">Content Scheduled</h4>
                    <p className="text-sm text-muted-foreground">When content is scheduled for publishing</p>
                  </div>
                  <Switch
                    checked={userData.notifications.contentScheduled}
                    onCheckedChange={(checked) => setUserData({
                      ...userData,
                      notifications: { ...userData.notifications, contentScheduled: checked }
                    })}
                  />
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <h4 className="font-medium">Content Published</h4>
                    <p className="text-sm text-muted-foreground">When content is published to platforms</p>
                  </div>
                  <Switch
                    checked={userData.notifications.contentPublished}
                    onCheckedChange={(checked) => setUserData({
                      ...userData,
                      notifications: { ...userData.notifications, contentPublished: checked }
                    })}
                  />
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <h4 className="font-medium">Interactions</h4>
                    <p className="text-sm text-muted-foreground">When someone interacts with your content</p>
                  </div>
                  <Switch
                    checked={userData.notifications.interactions}
                    onCheckedChange={(checked) => setUserData({
                      ...userData,
                      notifications: { ...userData.notifications, interactions: checked }
                    })}
                  />
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <h4 className="font-medium">Reports</h4>
                    <p className="text-sm text-muted-foreground">When analytics reports are generated</p>
                  </div>
                  <Switch
                    checked={userData.notifications.reports}
                    onCheckedChange={(checked) => setUserData({
                      ...userData,
                      notifications: { ...userData.notifications, reports: checked }
                    })}
                  />
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end">
              <Button onClick={handleSaveNotifications} disabled={isSaving}>
                {isSaving ? "Saving..." : "Save Preferences"}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="api" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>API Settings</CardTitle>
              <CardDescription>Configure AI and API settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="font-medium">OpenAI Configuration</h3>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="openaiApiKey">OpenAI API Key</Label>
                    <Input
                      id="openaiApiKey"
                      type="password"
                      value={apiSettings.openaiApiKey}
                      onChange={(e) => setApiSettings({ ...apiSettings, openaiApiKey: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="openaiModel">Model</Label>
                    <Select
                      value={apiSettings.openaiModel}
                      onValueChange={(value) => setApiSettings({ ...apiSettings, openaiModel: value })}
                    >
                      <SelectTrigger id="openaiModel">
                        <SelectValue placeholder="Select model" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="gpt-4o">GPT-4o</SelectItem>
                        <SelectItem value="gpt-4-turbo">GPT-4 Turbo</SelectItem>
                        <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="maxTokens">Max Tokens</Label>
                    <Input
                      id="maxTokens"
                      type="number"
                      value={apiSettings.maxTokens}
                      onChange={(e) => setApiSettings({ ...apiSettings, maxTokens: parseInt(e.target.value) })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="temperature">Temperature</Label>
                    <Input
                      id="temperature"
                      type="number"
                      step="0.1"
                      min="0"
                      max="1"
                      value={apiSettings.temperature}
                      onChange={(e) => setApiSettings({ ...apiSettings, temperature: parseFloat(e.target.value) })}
                    />
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-medium">Content Generation Settings</h3>
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="maxRetries">Max Retries</Label>
                    <Input
                      id="maxRetries"
                      type="number"
                      value={apiSettings.contentGeneration.maxRetries}
                      onChange={(e) => setApiSettings({
                        ...apiSettings,
                        contentGeneration: {
                          ...apiSettings.contentGeneration,
                          maxRetries: parseInt(e.target.value)
                        }
                      })}
                    />
                  </div>
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <h4 className="font-medium">Include Hashtags</h4>
                    <p className="text-sm text-muted-foreground">Automatically include relevant hashtags in generated content</p>
                  </div>
                  <Switch
                    checked={apiSettings.contentGeneration.includeHashtags}
                    onCheckedChange={(checked) => setApiSettings({
                      ...apiSettings,
                      contentGeneration: {
                        ...apiSettings.contentGeneration,
                        includeHashtags: checked
                      }
                    })}
                  />
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <h4 className="font-medium">Auto Schedule</h4>
                    <p className="text-sm text-muted-foreground">Automatically schedule generated content</p>
                  </div>
                  <Switch
                    checked={apiSettings.contentGeneration.autoSchedule}
                    onCheckedChange={(checked) => setApiSettings({
                      ...apiSettings,
                      contentGeneration: {
                        ...apiSettings.contentGeneration,
                        autoSchedule: checked
                      }
                    })}
                  />
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end">
              <Button onClick={handleSaveAPI} disabled={isSaving}>
                {isSaving ? "Saving..." : "Save API Settings"}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>

        <TabsContent value="platforms" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Platform Settings</CardTitle>
              <CardDescription>Configure platform-specific settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="font-medium">Default Platforms</h3>
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant={platformSettings.defaultPlatforms.includes("twitter") ? "default" : "outline"}
                    onClick={() => {
                      const newDefaults = platformSettings.defaultPlatforms.includes("twitter")
                        ? platformSettings.defaultPlatforms.filter(p => p !== "twitter")
                        : [...platformSettings.defaultPlatforms, "twitter"];
                      setplatformSettings({ ...platformSettings, defaultPlatforms: newDefaults });
                    }}
                  >
                    Twitter
                  </Button>
                  <Button
                    variant={platformSettings.defaultPlatforms.includes("linkedin") ? "default" : "outline"}
                    onClick={() => {
                      const newDefaults = platformSettings.defaultPlatforms.includes("linkedin")
                        ? platformSettings.defaultPlatforms.filter(p => p !== "linkedin")
                        : [...platformSettings.defaultPlatforms, "linkedin"];
                      setplatformSettings({ ...platformSettings, defaultPlatforms: newDefaults });
                    }}
                  >
                    LinkedIn
                  </Button>
                  <Button
                    variant={platformSettings.defaultPlatforms.includes("bluesky") ? "default" : "outline"}
                    onClick={() => {
                      const newDefaults = platformSettings.defaultPlatforms.includes("bluesky")
                        ? platformSettings.defaultPlatforms.filter(p => p !== "bluesky")
                        : [...platformSettings.defaultPlatforms, "bluesky"];
                      setplatformSettings({ ...platformSettings, defaultPlatforms: newDefaults });
                    }}
                  >
                    Bluesky
                  </Button>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-medium">Publishing Settings</h3>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <h4 className="font-medium">Auto Publish</h4>
                    <p className="text-sm text-muted-foreground">Automatically publish content when scheduled time arrives</p>
                  </div>
                  <Switch
                    checked={platformSettings.autoPublish}
                    onCheckedChange={(checked) => setplatformSettings({
                      ...platformSettings,
                      autoPublish: checked
                    })}
                  />
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <h4 className="font-medium">Require Approval</h4>
                    <p className="text-sm text-muted-foreground">Require manual approval before publishing content</p>
                  </div>
                  <Switch
                    checked={platformSettings.requireApproval}
                    onCheckedChange={(checked) => setplatformSettings({
                      ...platformSettings,
                      requireApproval: checked
                    })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="maxScheduledPerDay">Max Scheduled Per Day</Label>
                  <Input
                    id="maxScheduledPerDay"
                    type="number"
                    value={platformSettings.maxScheduledPerDay}
                    onChange={(e) => setplatformSettings({
                      ...platformSettings,
                      maxScheduledPerDay: parseInt(e.target.value)
                    })}
                  />
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-medium">Content Filters</h3>
                <div className="space-y-2">
                  <Label htmlFor="blacklistedWords">Blacklisted Words</Label>
                  <Textarea
                    id="blacklistedWords"
                    placeholder="Enter comma-separated words to blacklist"
                    value={platformSettings.blacklistedWords}
                    onChange={(e) => setplatformSettings({
                      ...platformSettings,
                      blacklistedWords: e.target.value
                    })}
                  />
                  <p className="text-sm text-muted-foreground">Content containing these words will be flagged for review</p>
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <h4 className="font-medium">Profanity Filter</h4>
                    <p className="text-sm text-muted-foreground">Filter out profanity from generated content</p>
                  </div>
                  <Switch
                    checked={platformSettings.contentFilters.profanityFilter}
                    onCheckedChange={(checked) => setplatformSettings({
                      ...platformSettings,
                      contentFilters: {
                        ...platformSettings.contentFilters,
                        profanityFilter: checked
                      }
                    })}
                  />
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <h4 className="font-medium">Sentiment Analysis</h4>
                    <p className="text-sm text-muted-foreground">Analyze sentiment of generated content</p>
                  </div>
                  <Switch
                    checked={platformSettings.contentFilters.sentimentAnalysis}
                    onCheckedChange={(checked) => setplatformSettings({
                      ...platformSettings,
                      contentFilters: {
                        ...platformSettings.contentFilters,
                        sentimentAnalysis: checked
                      }
                    })}
                  />
                </div>
                <div className="flex items-center justify-between rounded-lg border p-4">
                  <div>
                    <h4 className="font-medium">Brand Safety Check</h4>
                    <p className="text-sm text-muted-foreground">Check content for brand safety issues</p>
                  </div>
                  <Switch
                    checked={platformSettings.contentFilters.brandSafetyCheck}
                    onCheckedChange={(checked) => setplatformSettings({
                      ...platformSettings,
                      contentFilters: {
                        ...platformSettings.contentFilters,
                        brandSafetyCheck: checked
                      }
                    })}
                  />
                </div>
              </div>
            </CardContent>
            <CardFooter className="flex justify-end">
              <Button onClick={handleSavePlatforms} disabled={isSaving}>
                {isSaving ? "Saving..." : "Save Platform Settings"}
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
