export interface Document {
  id: string;
  name: string;
  type: 'file' | 'url' | 'youtube' | 'audio' | 'image';
  content?: string;
  url?: string;
  uploadedAt: Date;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface Conversation {
  id: string;
  documentId: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}
