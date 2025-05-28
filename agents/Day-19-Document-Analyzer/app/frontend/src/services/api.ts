import axios from 'axios';
import type {Document, Message} from '../types';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadDocument = async (file: File): Promise<Document> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const addDocumentUrl = async (url: string, name: string, type: string = 'url', useOcr: boolean = false, useLlmDescription: boolean = false): Promise<Document> => {
  const response = await api.post('/documents/url', { url, name, type, useOcr, useLlmDescription });
  return response.data;
};

export const getDocuments = async (): Promise<Document[]> => {
  const response = await api.get('/documents');
  return response.data;
};

export const getDocument = async (id: string): Promise<Document> => {
  const response = await api.get(`/documents/${id}`);
  return response.data;
};

export const analyzeDocument = async (
  documentId: string, 
  question: string
): Promise<{ user_message: Message, assistant_message: Message }> => {
  const response = await api.post(`/documents/${documentId}/analyze`, { question });
  return response.data;
};

export const getConversation = async (documentId: string): Promise<Message[]> => {
  const response = await api.get(`/documents/${documentId}/conversation`);
  return response.data;
};

export default api;
