import apiClient from "./client";

export interface PlatformConnection {
  id: number;
  platform_name: string;
  platform_id: string;
  username: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Content {
  id: number;
  title: string;
  body: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Interaction {
  id: number;
  type: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface Persona {
  id: number;
  name: string;
  background: string;
  interests: string[];
  values: string[];
  tone: string;
  expertise: string[];
  purpose: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  avatar_url?: string;
  platform_connections?: PlatformConnection[];
  content?: Content[];
  interactions?: Interaction[];
  owner_id?: number;
}

export interface PersonaCreate {
  name: string;
  background: string;
  interests: string[];
  values: string[];
  tone: string;
  expertise: string[];
  purpose: string;
  is_active?: boolean;
}

export interface PersonaUpdate {
  name?: string;
  background?: string;
  interests?: string[];
  values?: string[];
  tone?: string;
  expertise?: string[];
  purpose?: string;
  is_active?: boolean;
}

export interface PersonaListResponse {
  items: Persona[];
  total: number;
  skip: number;
  limit: number;
}

const personaService = {
  // Get all personas
  getPersonas: async (params?: { skip?: number; limit?: number; active_only?: boolean }) => {
    const response = await apiClient.get<PersonaListResponse>("/personas", { params });
    return response.data;
  },

  // Get a persona by ID
  getPersona: async (id: number) => {
    const response = await apiClient.get<Persona>(`/personas/${id}`);
    return response.data;
  },

  // Create a new persona
  createPersona: async (persona: PersonaCreate) => {
    const response = await apiClient.post<Persona>("/personas", persona);
    return response.data;
  },

  // Update a persona
  updatePersona: async (id: number, persona: PersonaUpdate) => {
    const response = await apiClient.put<Persona>(`/personas/${id}`, persona);
    return response.data;
  },

  // Delete a persona
  deletePersona: async (id: number) => {
    const response = await apiClient.delete(`/personas/${id}`);
    return response.data;
  },

  // Set active persona
  setActivePersona: (id: number) => {
    localStorage.setItem("active_persona_id", id.toString());
  },

  // Get active persona ID
  getActivePersonaId: (): number | null => {
    const id = localStorage.getItem("active_persona_id");
    return id ? parseInt(id, 10) : null;
  },
};

export default personaService;
