import api from './api';

export interface Resource {
  id: string;
  title: string;
  url: string;
  type: string;
  description: string;
  difficulty: string;
  estimated_time: string;
  topics: string[];
  source: string;
  created_at?: string;
  user_id?: number;
}

export interface ResourcesResponse {
  resources: Resource[];
  query?: string;
  total_count: number;
}

export interface CreateResourceRequest {
  title: string;
  url: string;
  type: string;
  description: string;
  difficulty: string;
  estimated_time: string;
  topics: string[];
  source: string;
  user_id?: number;
}

export const getResources = async (
  topic?: string,
  type?: string,
  difficulty?: string
): Promise<Resource[]> => {
  let url = '/resources';
  const params = new URLSearchParams();
  
  if (topic) params.append('topic', topic);
  if (type) params.append('resource_type', type);
  if (difficulty) params.append('difficulty', difficulty);
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await api.get<Resource[]>(url);
  return response.data;
};

export const getResource = async (id: string): Promise<Resource> => {
  const response = await api.get<Resource>(`/resources/${id}`);
  return response.data;
};

export const createResource = async (resource: CreateResourceRequest): Promise<Resource> => {
  const response = await api.post<Resource>('/resources', resource);
  return response.data;
};

export const updateResource = async (id: string, resource: Partial<CreateResourceRequest>): Promise<Resource> => {
  const response = await api.put<Resource>(`/resources/${id}`, resource);
  return response.data;
};

export const deleteResource = async (id: string): Promise<void> => {
  await api.delete(`/resources/${id}`);
};

// Function to save resources from the chat interface
export const saveResourcesFromChat = async (resources: any[]): Promise<Resource[]> => {
  // Transform the resources from the chat format to the API format if needed
  const createRequests: CreateResourceRequest[] = resources.map(resource => ({
    title: resource.title,
    url: resource.url,
    type: resource.type,
    description: resource.description || '',
    difficulty: resource.difficulty || 'beginner',
    estimated_time: resource.estimated_time || 'unknown',
    topics: resource.topics || [],
    source: resource.source || new URL(resource.url).hostname
  }));
  
  // Create all resources
  const createdResources: Resource[] = [];
  for (const request of createRequests) {
    const resource = await createResource(request);
    createdResources.push(resource);
  }
  
  return createdResources;
};
