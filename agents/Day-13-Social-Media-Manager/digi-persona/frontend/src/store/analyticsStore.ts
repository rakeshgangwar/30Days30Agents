import { create } from "zustand";
import analyticsService from "@/api/analyticsService";

export interface EngagementDataPoint {
  date: string;
  twitter?: number;
  linkedin?: number;
  bluesky?: number;
  [key: string]: any;
}

export interface ContentTypeItem {
  name: string;
  value: number;
}

export interface InteractionTypeItem {
  name: string;
  value: number;
}

export interface PlatformItem {
  name: string;
  posts: number;
  engagement: number;
  followers: number;
}

export interface PersonaPerformanceItem {
  id: number;
  name: string;
  avatar?: string;
  posts: number;
  engagement: number;
  followers: number;
}

export interface AnalyticsData {
  engagement: EngagementDataPoint[];
  content_types: ContentTypeItem[];
  interaction_types: InteractionTypeItem[];
  platforms: PlatformItem[];
  personas: PersonaPerformanceItem[];
}

export type TimeRange = "1w" | "2w" | "1m" | "3m";

interface AnalyticsState {
  data: AnalyticsData | null;
  isLoading: boolean;
  error: string | null;
  isRealtime: boolean;
  websocket: WebSocket | null;
  timeRange: TimeRange;
  selectedPersonaId: number | null;
  selectedPlatform: string | null;
  
  // Actions
  fetchAnalytics: (params?: {
    persona_id?: number;
    platform?: string;
    time_range?: TimeRange;
  }) => Promise<void>;
  
  startRealtimeUpdates: () => void;
  stopRealtimeUpdates: () => void;
  
  setTimeRange: (timeRange: TimeRange) => void;
  setSelectedPersonaId: (personaId: number | null) => void;
  setSelectedPlatform: (platform: string | null) => void;
}

export const useAnalyticsStore = create<AnalyticsState>((set, get) => ({
  data: null,
  isLoading: false,
  error: null,
  isRealtime: false,
  websocket: null,
  timeRange: "2w",
  selectedPersonaId: null,
  selectedPlatform: null,
  
  fetchAnalytics: async (params) => {
    set({ isLoading: true, error: null });
    
    try {
      const response = await analyticsService.getDashboardData({
        persona_id: params?.persona_id || get().selectedPersonaId,
        platform: params?.platform || get().selectedPlatform,
        time_range: params?.time_range || get().timeRange,
      });
      
      set({ 
        data: response,
        isLoading: false 
      });
      
      return response;
    } catch (error) {
      console.error("Error fetching analytics data:", error);
      set({ 
        error: "Failed to fetch analytics data", 
        isLoading: false 
      });
    }
  },
  
  startRealtimeUpdates: () => {
    // Close existing connection if any
    if (get().websocket) {
      get().stopRealtimeUpdates();
    }
    
    try {
      // Create WebSocket connection
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = import.meta.env.VITE_API_URL?.replace(/^https?:\/\//, '') || 'localhost:8000/api/v1';
      const ws = new WebSocket(`${protocol}//${host}/analytics/ws`);
      
      // Set up event handlers
      ws.onopen = () => {
        console.log("WebSocket connection established");
        set({ isRealtime: true });
        
        // Send initial parameters
        ws.send(JSON.stringify({
          persona_id: get().selectedPersonaId,
          platform: get().selectedPlatform,
          time_range: get().timeRange,
        }));
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        set({ data });
      };
      
      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        set({ 
          error: "WebSocket connection error", 
          isRealtime: false 
        });
      };
      
      ws.onclose = () => {
        console.log("WebSocket connection closed");
        set({ isRealtime: false });
      };
      
      // Store WebSocket instance
      set({ websocket: ws });
    } catch (error) {
      console.error("Error setting up WebSocket:", error);
      set({ 
        error: "Failed to set up real-time updates", 
        isRealtime: false 
      });
    }
  },
  
  stopRealtimeUpdates: () => {
    const { websocket } = get();
    
    if (websocket) {
      websocket.close();
      set({ websocket: null, isRealtime: false });
    }
  },
  
  setTimeRange: (timeRange) => {
    set({ timeRange });
    
    // Update WebSocket parameters if connected
    const { websocket, isRealtime } = get();
    if (websocket && isRealtime) {
      websocket.send(JSON.stringify({
        persona_id: get().selectedPersonaId,
        platform: get().selectedPlatform,
        time_range: timeRange,
      }));
    }
  },
  
  setSelectedPersonaId: (personaId) => {
    set({ selectedPersonaId: personaId });
    
    // Update WebSocket parameters if connected
    const { websocket, isRealtime } = get();
    if (websocket && isRealtime) {
      websocket.send(JSON.stringify({
        persona_id: personaId,
        platform: get().selectedPlatform,
        time_range: get().timeRange,
      }));
    }
  },
  
  setSelectedPlatform: (platform) => {
    set({ selectedPlatform: platform });
    
    // Update WebSocket parameters if connected
    const { websocket, isRealtime } = get();
    if (websocket && isRealtime) {
      websocket.send(JSON.stringify({
        persona_id: get().selectedPersonaId,
        platform,
        time_range: get().timeRange,
      }));
    }
  },
}));
