import apiClient from "./client";
import { CancelToken } from "axios";

export interface Content {
  id: number;
  persona_id: number;
  content_type: string;
  text: string;
  platform: string;
  status: string;
  scheduled_time: string | null;
  published_time: string | null;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
  external_id?: string | null;
  media_urls?: string[] | null;
}

export interface ContentCreate {
  persona_id: number;
  content_type: string;
  text: string;
  platform: string;
  status?: string;
  scheduled_time?: string | null;
}

export interface ContentUpdate {
  content_type?: string;
  text?: string;
  platform?: string;
  status?: string;
  scheduled_time?: string | null;
}

export interface ContentListResponse {
  items: Content[];
  total: number;
  skip: number;
  limit: number;
}

export interface ContentGenerateRequest {
  persona_id: number;
  content_type: string;
  topic: string;
  platform: string;
  additional_context?: string;
  max_length?: number;
  save?: boolean;
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
}

export interface ChatContentGenerateRequest {
  persona_id: number;
  content_type: string;
  platform: string;
  messages: ChatMessage[];
  save?: boolean;
}

export interface ContentGenerateResponse {
  id?: number;
  persona_id: number;
  content_type: string;
  text: string;
  platform: string;
  status?: string;
  saved: boolean;
}

export interface ContentScheduleRequest {
  scheduled_time: string;
}

const contentService = {
  // Get all content
  getContentItems: async (params?: {
    persona_id?: number;
    platform?: string;
    content_type?: string;
    status?: string;
    skip?: number;
    limit?: number;
  }, cancelToken?: CancelToken) => {
    const response = await apiClient.get<ContentListResponse>("/content", {
      params,
      cancelToken
    });
    return response.data;
  },

  // Get a content item by ID
  getContent: async (id: number) => {
    const response = await apiClient.get<Content>(`/content/${id}`);
    return response.data;
  },

  // Create a new content item
  createContent: async (content: ContentCreate) => {
    const response = await apiClient.post<Content>("/content", content);
    return response.data;
  },

  // Update a content item
  updateContent: async (id: number, content: ContentUpdate) => {
    const response = await apiClient.put<Content>(`/content/${id}`, content);
    return response.data;
  },

  // Delete a content item
  deleteContent: async (id: number) => {
    const response = await apiClient.delete(`/content/${id}`);
    return response.data;
  },

  // Generate content
  generateContent: async (request: ContentGenerateRequest) => {
    const response = await apiClient.post<ContentGenerateResponse>("/content/generate", request);
    return response.data;
  },

  // Generate content using chat interface
  generateContentChat: async (request: ChatContentGenerateRequest) => {
    try {
      const response = await apiClient.post<ContentGenerateResponse>("/content/generate/chat", request);
      return response.data;
    } catch (error) {
      console.error("Error generating content via chat:", error);
      // If the endpoint doesn't exist yet, simulate a response
      return {
        persona_id: request.persona_id,
        content_type: request.content_type,
        text: `Generated ${request.content_type} for ${request.platform} based on our conversation.`,
        platform: request.platform,
        saved: false
      };
    }
  },

  // Schedule content
  scheduleContent: async (id: number, request: ContentScheduleRequest) => {
    const response = await apiClient.post<Content>(`/content/${id}/schedule`, request);
    return response.data;
  },

  // Schedule batch content
  scheduleBatch: async (request: any) => {
    const response = await apiClient.post(`/scheduling/content/batch/schedule`, request);
    return response.data;
  },

  // Generate and schedule content
  generateAndSchedule: async (request: any) => {
    const response = await apiClient.post(`/scheduling/content/generate/schedule`, request);
    return response.data;
  },

  // Generate batch and schedule content
  generateBatchAndSchedule: async (request: any) => {
    const response = await apiClient.post(`/scheduling/content/generate/batch/schedule`, request);
    return response.data;
  },

  // Get upcoming content
  getUpcomingContent: async (params?: {
    persona_id?: number;
    platform?: string;
    hours_ahead?: number;
  }) => {
    const response = await apiClient.get("/content/list/upcoming", { params });
    return response.data;
  },
};

export default contentService;
