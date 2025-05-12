import api from './api';

interface AgentRequest {
  user_input: string;
  user_id?: number;
  context?: Record<string, any>;
}

interface AgentResponse {
  response: string;
  response_type: string;
  context: Record<string, any>;
}

export const chatWithAgent = async (request: AgentRequest): Promise<AgentResponse> => {
  const response = await api.post<AgentResponse>('/agent/chat', request);
  return response.data;
};
