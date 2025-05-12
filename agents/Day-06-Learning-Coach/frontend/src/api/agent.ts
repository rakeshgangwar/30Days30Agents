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
  // Ensure context is included in the request
  const requestWithContext = {
    ...request,
    context: request.context || {}
  };

  const response = await api.post<AgentResponse>('/agent/chat', requestWithContext);
  return response.data;
};
