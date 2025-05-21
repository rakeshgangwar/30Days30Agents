import apiClient from "./client";

export interface InteractionAuthor {
  id?: string;
  name?: string;
  username?: string;
  screen_name?: string;
  handle?: string;
  profile_image_url?: string;
  display_name?: string;
  [key: string]: string | undefined;
}

export interface Interaction {
  id: number;
  persona_id: number;
  platform: string;
  external_id: string;
  type: string;
  content: string;
  author: InteractionAuthor;
  status: string;
  response?: string;
  created_at: string;
  updated_at: string;
  responded_at?: string;
  platform_data?: Record<string, unknown>;
}

export interface InteractionList {
  items: Interaction[];
  total: number;
  skip: number;
  limit: number;
}

export interface InteractionFilter {
  persona_id?: number;
  platform?: string;
  status?: string;
  type?: string;
  author_name?: string;
  content_contains?: string;
  created_after?: string;
  created_before?: string;
  sort_by?: string;
  sort_order?: string;
}

export interface InteractionResponseCreate {
  content: string;
}

export interface InteractionResponseResult {
  interaction_id: number;
  platform: string;
  content: string;
  external_id: string;
  created_at?: string;
  platform_data?: Record<string, unknown>;
}

export interface SyncResult {
  platforms: Record<string, {
    persona_id: number;
    new_interactions?: number;
    error?: string;
  }>;
  total_new_interactions: number;
}

const interactionService = {
  // Get all interactions
  getInteractions: async (params?: {
    persona_id?: number;
    platform?: string;
    status?: string;
    type?: string;
    skip?: number;
    limit?: number;
  }) => {
    const response = await apiClient.get<InteractionList>("/interactions", { params });
    return response.data;
  },

  // Get a specific interaction
  getInteraction: async (id: number) => {
    const response = await apiClient.get<Interaction>(`/interactions/${id}`);
    return response.data;
  },

  // Sync interactions from platforms
  syncInteractions: async (params?: {
    platform_filter?: string;
    persona_id?: number;
    count?: number;
  }) => {
    const response = await apiClient.post<SyncResult>("/interactions/sync", undefined, { params });
    return response.data;
  },

  // Respond to an interaction
  respondToInteraction: async (id: number, responseData: InteractionResponseCreate) => {
    const response = await apiClient.post<InteractionResponseResult>(
      `/interactions/${id}/respond`,
      responseData
    );
    return response.data;
  },

  // Generate AI response for an interaction
  generateResponse: async (id: number) => {
    const response = await apiClient.post<{ generated_response: string }>(
      "/interactions/generate-response",
      undefined,
      { params: { interaction_id: id } }
    );
    return response.data;
  },

  // Filter interactions
  filterInteractions: async (filter: InteractionFilter, skip = 0, limit = 100) => {
    const response = await apiClient.post<InteractionList>("/interactions/filter", filter, {
      params: { skip, limit }
    });
    return response.data;
  }
};

export default interactionService;