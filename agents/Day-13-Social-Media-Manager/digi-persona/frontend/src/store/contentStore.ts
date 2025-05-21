import { create } from "zustand";
import { Content, ContentGenerateRequest, ChatContentGenerateRequest } from "@/api/contentService";
import contentService from "@/api/contentService";
import axios, { CancelTokenSource } from "axios";

interface ContentState {
  contentItems: Content[];
  upcomingContent: Content[];
  isLoading: boolean;
  error: string | null;
  fetchContentItems: (params?: any) => Promise<void>;
  fetchUpcomingContent: (params?: any) => Promise<void>;
  generateContent: (request: ContentGenerateRequest) => Promise<any>;
  generateContentChat: (request: ChatContentGenerateRequest) => Promise<any>;
  createContent: (content: any) => Promise<Content>;
  updateContent: (id: number, content: any) => Promise<Content>;
  deleteContent: (id: number) => Promise<void>;
  scheduleContent: (id: number, scheduleData: any) => Promise<Content>;
  scheduleBatch: (scheduleData: any) => Promise<any>;
  generateAndSchedule: (scheduleData: any) => Promise<any>;
  generateBatchAndSchedule: (scheduleData: any) => Promise<any>;
}

// Create a private variable to store the cancel token outside the store
let cancelToken: CancelTokenSource | null = null;

export const useContentStore = create<ContentState>((set, get) => ({
  contentItems: [],
  upcomingContent: [],
  isLoading: false,
  error: null,

  fetchContentItems: async (params?: any) => {
    // Cancel any ongoing requests
    if (cancelToken) {
      cancelToken.cancel('Operation canceled due to new request');
    }

    // Create a new cancel token
    const newCancelToken = axios.CancelToken.source();
    cancelToken = newCancelToken;
    set({ isLoading: true, error: null });

    try {
      const response = await contentService.getContentItems(params, newCancelToken.token);
      // Set the content items
      set({ contentItems: response.items, isLoading: false });
    } catch (error: any) {
      // Don't update state if the request was canceled
      if (axios.isCancel(error)) {
        console.log('Request canceled:', error.message);
        return;
      }

      // Update error state
      set({ error: "Failed to fetch content items", isLoading: false });
      console.error("Error fetching content items:", error);
    }
  },

  fetchUpcomingContent: async (params?: any) => {
    set({ isLoading: true, error: null });
    try {
      const response = await contentService.getUpcomingContent(params);
      set({ upcomingContent: response, isLoading: false });
    } catch (error) {
      set({ error: "Failed to fetch upcoming content", isLoading: false });
      console.error("Error fetching upcoming content:", error);
    }
  },

  generateContent: async (request: ContentGenerateRequest) => {
    set({ isLoading: true, error: null });
    try {
      const response = await contentService.generateContent(request);
      set({ isLoading: false });
      return response;
    } catch (error) {
      set({ error: "Failed to generate content", isLoading: false });
      console.error("Error generating content:", error);
      throw error;
    }
  },

  generateContentChat: async (request: ChatContentGenerateRequest) => {
    set({ isLoading: true, error: null });
    try {
      const response = await contentService.generateContentChat(request);
      set({ isLoading: false });
      return response;
    } catch (error) {
      set({ error: "Failed to generate content from chat", isLoading: false });
      console.error("Error generating content from chat:", error);
      throw error;
    }
  },

  createContent: async (content: any) => {
    set({ isLoading: true, error: null });
    try {
      const newContent = await contentService.createContent(content);
      set(state => ({
        contentItems: [...state.contentItems, newContent],
        isLoading: false
      }));
      return newContent;
    } catch (error) {
      set({ error: "Failed to create content", isLoading: false });
      console.error("Error creating content:", error);
      throw error;
    }
  },

  updateContent: async (id: number, content: any) => {
    set({ isLoading: true, error: null });
    try {
      const updatedContent = await contentService.updateContent(id, content);
      console.log('Updated content from API:', updatedContent);
      set(state => ({
        contentItems: Array.isArray(state.contentItems)
          ? state.contentItems.map(c => c.id === id ? updatedContent : c)
          : [],
        upcomingContent: Array.isArray(state.upcomingContent)
          ? state.upcomingContent.map(c => c.id === id ? updatedContent : c)
          : [],
        isLoading: false
      }));
      return updatedContent;
    } catch (error) {
      set({ error: "Failed to update content", isLoading: false });
      console.error("Error updating content:", error);
      throw error;
    }
  },

  deleteContent: async (id: number) => {
    set({ isLoading: true, error: null });
    try {
      await contentService.deleteContent(id);
      set(state => ({
        contentItems: state.contentItems.filter(c => c.id !== id),
        upcomingContent: state.upcomingContent.filter(c => c.id !== id),
        isLoading: false
      }));
    } catch (error) {
      set({ error: "Failed to delete content", isLoading: false });
      console.error("Error deleting content:", error);
      throw error;
    }
  },

  scheduleContent: async (id: number, scheduleData: any) => {
    set({ isLoading: true, error: null });
    try {
      const scheduledContent = await contentService.scheduleContent(id, scheduleData);
      set(state => ({
        contentItems: state.contentItems.map(c => c.id === id ? scheduledContent : c),
        isLoading: false
      }));
      return scheduledContent;
    } catch (error) {
      set({ error: "Failed to schedule content", isLoading: false });
      console.error("Error scheduling content:", error);
      throw error;
    }
  },

  scheduleBatch: async (scheduleData: any) => {
    set({ isLoading: true, error: null });
    try {
      const response = await contentService.scheduleBatch(scheduleData);
      set({ isLoading: false });
      return response;
    } catch (error) {
      set({ error: "Failed to schedule batch content", isLoading: false });
      console.error("Error scheduling batch content:", error);
      throw error;
    }
  },

  generateAndSchedule: async (scheduleData: any) => {
    set({ isLoading: true, error: null });
    try {
      const response = await contentService.generateAndSchedule(scheduleData);
      set({ isLoading: false });
      return response;
    } catch (error) {
      set({ error: "Failed to generate and schedule content", isLoading: false });
      console.error("Error generating and scheduling content:", error);
      throw error;
    }
  },

  generateBatchAndSchedule: async (scheduleData: any) => {
    set({ isLoading: true, error: null });
    try {
      const response = await contentService.generateBatchAndSchedule(scheduleData);
      set({ isLoading: false });
      return response;
    } catch (error) {
      set({ error: "Failed to generate and schedule batch content", isLoading: false });
      console.error("Error generating and scheduling batch content:", error);
      throw error;
    }
  }
}));
