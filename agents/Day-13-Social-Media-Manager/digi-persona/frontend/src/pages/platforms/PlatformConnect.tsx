import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import personaService from "@/api/personaService";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { usePersonaStore } from "@/store/personaStore";
import platformService, { PlatformConnectionCreate, PlatformCredentials } from "@/api/platformService";

interface PlatformFormData {
  personaId: string;
  platform: string;
  username: string;
  apiKey: string;
  apiSecret: string;
  accessToken: string;
  accessTokenSecret: string;
  appPassword: string;
  handle: string;
}
export function PlatformConnect() {
  const navigate = useNavigate();
  const { personas, activePersona, fetchPersonas } = usePersonaStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState("twitter");
  
  // Fetch personas when component mounts
  useEffect(() => {
    console.log("Fetching personas...");
    fetchPersonas()
      .then(() => console.log("Personas fetched successfully"))
      .catch(error => console.error("Error fetching personas:", error));
  }, [fetchPersonas]);

  const form = useForm<PlatformFormData>({
    defaultValues: {
      personaId: activePersona ? activePersona.id.toString() : "",
      platform: "twitter",
      username: "",
      apiKey: "",
      apiSecret: "",
      accessToken: "",
      accessTokenSecret: "",
      appPassword: "",  // for Bluesky
      handle: "",       // for Bluesky
    },
  });

  const onSubmit = async (data: PlatformFormData) => {
    setIsSubmitting(true);
    try {
      // Ensure we have a valid persona ID and it's set in localStorage
      if (!data.personaId) {
        throw new Error("No persona selected");
      }
      
      // Set the active persona ID in localStorage to ensure it's included in API headers
      personaService.setActivePersona(parseInt(data.personaId));
      
      // Create platform connection data
      const connectionData: PlatformConnectionCreate = {
        platform_name: data.platform,
        username: data.username,
        credentials: {} as PlatformCredentials
      };

      // Add platform-specific credentials
      switch (data.platform) {
        case "twitter":
          connectionData.credentials = {
            api_key: data.apiKey,
            api_secret: data.apiSecret,
            access_token: data.accessToken,
            access_token_secret: data.accessTokenSecret
          };
          break;
        case "linkedin":
          connectionData.credentials = {
            client_id: data.apiKey,
            client_secret: data.apiSecret,
            access_token: data.accessToken
          };
          break;
        case "bluesky":
          connectionData.credentials = {
            app_password: data.apiKey,
            handle: data.username
          };
          break;
        default:
          break;
      }

      // Make the API call to connect the platform
      const response = await platformService.connectPlatform(connectionData);
      console.log("Platform connection response:", response);
      
      // Only show success message and navigate if we actually get a response
      if (response && response.id) {
        toast.success(`Connected to ${data.platform} successfully`);
        navigate("/platforms");
      } else {
        // This shouldn't happen if the API call succeeds, but just in case
        toast.error(`Failed to connect to ${data.platform}: No valid response`);
      }
    } catch (error) {
      toast.error(`Failed to connect to ${data.platform}: ${error instanceof Error ? error.message : 'Unknown error'}`);
      console.error("Error connecting platform:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePlatformChange = (value: string) => {
    setSelectedPlatform(value);
    form.setValue("platform", value);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Connect Platform</h1>
        <Button variant="outline" onClick={() => navigate("/platforms")}>
          Cancel
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Connect Social Media Platform</CardTitle>
          <CardDescription>Connect a social media platform to one of your personas</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="twitter" value={selectedPlatform} onValueChange={handlePlatformChange}>
            <TabsList className="mb-4">
              <TabsTrigger value="twitter">Twitter</TabsTrigger>
              <TabsTrigger value="linkedin">LinkedIn</TabsTrigger>
              <TabsTrigger value="bluesky">Bluesky</TabsTrigger>
            </TabsList>

            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <FormField
                  control={form.control}
                  name="personaId"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Persona</FormLabel>
                      <Select
                        value={field.value.toString()}
                        onValueChange={field.onChange}
                        disabled={isSubmitting}
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
                        Select the persona to connect this platform to
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="username"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Username</FormLabel>
                      <FormControl>
                        <Input
                          placeholder={`Enter your ${selectedPlatform} username`}
                          {...field}
                          disabled={isSubmitting}
                        />
                      </FormControl>
                      <FormDescription>
                        Your username on {selectedPlatform}
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <TabsContent value="twitter" className="space-y-6 mt-6">
                  <div className="grid gap-6 sm:grid-cols-2">
                    <FormField
                      control={form.control}
                      name="apiKey"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>API Key</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Enter Twitter API Key"
                              type="password"
                              {...field}
                              disabled={isSubmitting}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="apiSecret"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>API Secret</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Enter Twitter API Secret"
                              type="password"
                              {...field}
                              disabled={isSubmitting}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <div className="grid gap-6 sm:grid-cols-2">
                    <FormField
                      control={form.control}
                      name="accessToken"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Access Token</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Enter Twitter Access Token"
                              type="password"
                              {...field}
                              disabled={isSubmitting}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="accessTokenSecret"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Access Token Secret</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Enter Twitter Access Token Secret"
                              type="password"
                              {...field}
                              disabled={isSubmitting}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </TabsContent>

                <TabsContent value="linkedin" className="space-y-6 mt-6">
                  <div className="grid gap-6 sm:grid-cols-2">
                    <FormField
                      control={form.control}
                      name="apiKey"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Client ID</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Enter LinkedIn Client ID"
                              type="password"
                              {...field}
                              disabled={isSubmitting}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="apiSecret"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Client Secret</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="Enter LinkedIn Client Secret"
                              type="password"
                              {...field}
                              disabled={isSubmitting}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>

                  <FormField
                    control={form.control}
                    name="accessToken"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Access Token</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Enter LinkedIn Access Token"
                            type="password"
                            {...field}
                            disabled={isSubmitting}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </TabsContent>

                <TabsContent value="bluesky" className="space-y-6 mt-6">
                  <FormField
                    control={form.control}
                    name="apiKey"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>App Password</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="Enter Bluesky App Password"
                            type="password"
                            {...field}
                            disabled={isSubmitting}
                          />
                        </FormControl>
                        <FormDescription>
                          Generate an app password in your Bluesky account settings
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </TabsContent>

                <div className="flex justify-end">
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? "Connecting..." : "Connect Platform"}
                  </Button>
                </div>
              </form>
            </Form>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
