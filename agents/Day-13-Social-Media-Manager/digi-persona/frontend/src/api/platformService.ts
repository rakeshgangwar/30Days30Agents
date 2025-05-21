import apiClient from "./client";

export interface PlatformConnection {
  id: number;
  persona_id: number;
  platform_name: string;
  platform_id: string;
  username: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  metrics: {
    follower_count: number;
    following_count: number;
    post_count: number;
  };
}

export interface PlatformCredentials {
  api_key?: string;
  api_secret?: string;
  access_token?: string;
  access_token_secret?: string;
  app_password?: string;
  client_id?: string;
  client_secret?: string;
  handle?: string;
  organization_id?: string;
  [key: string]: string | undefined;
}

export interface PlatformConnectionCreate {
  platform_name: string;
  username: string;
  credentials: PlatformCredentials;
}

export interface PlatformConnectionList {
  items: PlatformConnection[];
  total: number;
}

export interface PlatformMediaItem {
  url: string;
  type?: string;
  id?: string;
}

export interface PlatformUserInfo {
  id?: string;
  name?: string;
  handle?: string;
  screen_name?: string;
  profile_image_url?: string;
  [key: string]: string | undefined;
}

export interface PlatformPost {
  content: string;
  media_urls?: string[];
  additional_params?: Record<string, string | boolean | number>;
}

export interface PlatformPostResponse {
  platform_connection_id: number;
  platform_name: string;
  created_at: string;
  external_id: string;
  external_url?: string;
  content?: string;
  user?: PlatformUserInfo;
  media?: PlatformMediaItem[];
}

export interface PlatformAccountInfo {
  platform_connection_id: number;
  platform_name: string;
  platform_id: string;
  username: string;
  display_name?: string;
  description?: string;
  follower_count: number;
  following_count: number;
  post_count: number;
  profile_image_url?: string;
}

const platformService = {
  // Get all platform connections
  getPlatformConnections: async (params?: { active_only?: boolean }) => {
    const response = await apiClient.get<PlatformConnectionList>("/platforms", { params });
    return response.data;
  },

  // Get a platform connection by ID
  getPlatformConnection: async (id: number) => {
    const response = await apiClient.get<PlatformConnection>(`/platforms/${id}`);
    return response.data;
  },

  // Connect a new platform
  connectPlatform: async (platformData: PlatformConnectionCreate) => {
    try {
      console.log("Connecting platform with data:", platformData);
      console.log("Active persona ID:", localStorage.getItem("active_persona_id"));
      const response = await apiClient.post<PlatformConnection>("/platforms/connect", platformData);
      console.log("Platform connection successful:", response.data);
      return response.data;
    } catch (error) {
      console.error("Error connecting platform:", error);
      throw error;
    }
  },

  // Disconnect a platform
  disconnectPlatform: async (id: number) => {
    const response = await apiClient.post(`/platforms/${id}/disconnect`);
    return response.data;
  },

  // Get account information for a platform
  getPlatformAccountInfo: async (id: number) => {
    const response = await apiClient.get<PlatformAccountInfo>(`/platforms/${id}/account-info`);
    return response.data;
  },

  // Post content to a platform
  postToPlatform: async (id: number, postData: PlatformPost) => {
    const response = await apiClient.post<PlatformPostResponse>(`/platforms/${id}/post`, postData);
    return response.data;
  },

  // Sync platform data
  syncPlatform: async (id: number) => {
    const response = await apiClient.get(`/platforms/${id}/sync`);
    return response.data;
  }
};

export default platformService;