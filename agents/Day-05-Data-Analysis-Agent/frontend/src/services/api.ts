import axios from 'axios';
import type {
  CSVUploadResponse,
  DBConnectionRequest,
  DBConnectionResponse,
  QueryRequest,
  QueryResponse
} from '../types/index';

// Create axios instance with base URL
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
const endpoints = {
  // Health check
  healthCheck: () => api.get('/'),

  // CSV endpoints
  uploadCSV: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    return api.post<CSVUploadResponse>('/csv/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  queryCSV: (csvId: string, query: string) => {
    const formData = new FormData();
    formData.append('csv_id', csvId);
    formData.append('query', query);

    return api.post<QueryResponse>('/csv/query', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Database endpoints
  connectToDatabase: (request: DBConnectionRequest) => {
    return api.post<DBConnectionResponse>('/db/connect', request);
  },

  queryDatabase: (connectionId: string, request: QueryRequest) => {
    return api.post<QueryResponse>(`/db/query?connection_id=${connectionId}`, request);
  },

  // LLM test endpoint
  testLLM: () => api.get('/test-llm'),
};

export default endpoints;
