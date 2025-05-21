import apiClient from "./client";
import { AnalyticsData, TimeRange } from "@/store/analyticsStore";

const analyticsService = {
  // Get engagement data over time
  getEngagementData: async (params?: {
    persona_id?: number;
    platform?: string;
    time_range?: TimeRange;
  }) => {
    const response = await apiClient.get("/analytics/engagement", { params });
    return response.data;
  },

  // Get content type distribution
  getContentTypeData: async (params?: {
    persona_id?: number;
    platform?: string;
    time_range?: TimeRange;
  }) => {
    const response = await apiClient.get("/analytics/content-types", { params });
    return response.data;
  },

  // Get interaction type distribution
  getInteractionTypeData: async (params?: {
    persona_id?: number;
    platform?: string;
    time_range?: TimeRange;
  }) => {
    const response = await apiClient.get("/analytics/interaction-types", { params });
    return response.data;
  },

  // Get platform performance data
  getPlatformData: async (params?: {
    persona_id?: number;
    time_range?: TimeRange;
  }) => {
    const response = await apiClient.get("/analytics/platforms", { params });
    return response.data;
  },

  // Get persona performance data
  getPersonaPerformanceData: async (params?: {
    time_range?: TimeRange;
  }) => {
    const response = await apiClient.get("/analytics/personas", { params });
    return response.data;
  },

  // Get all dashboard data in one request
  getDashboardData: async (params?: {
    persona_id?: number | null;
    platform?: string | null;
    time_range?: TimeRange;
  }): Promise<AnalyticsData> => {
    // Filter out null values
    const filteredParams = Object.fromEntries(
      Object.entries(params || {}).filter(([_, v]) => v != null)
    );
    
    const response = await apiClient.get("/analytics/dashboard", { 
      params: filteredParams 
    });
    return response.data;
  },

  // Generate analytics report
  generateReport: async (params: {
    title: string;
    type: string;
    persona_id?: number;
    platform?: string;
    date_range: string;
    format: string;
  }) => {
    const response = await apiClient.post("/analytics/reports/generate", params);
    return response.data;
  },

  // Get list of reports
  getReports: async () => {
    const response = await apiClient.get("/analytics/reports");
    return response.data;
  },

  // Download a report
  downloadReport: async (reportId: string) => {
    const response = await apiClient.get(`/analytics/reports/${reportId}/download`, {
      responseType: "blob"
    });
    return response.data;
  }
};

export default analyticsService;
