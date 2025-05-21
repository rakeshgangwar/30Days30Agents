import apiClient from "./client";

export interface SuggestionRequest {
  content: string;
  persona_id?: number;
  content_type?: string;
  platform?: string;
  suggestion_type: string;
}

export interface Suggestion {
  id: string;
  text: string;
  type: string;
  description?: string;
}

export interface SuggestionResponse {
  suggestions: Suggestion[];
}

const aiSuggestionsService = {
  // Get content suggestions
  getSuggestions: async (request: SuggestionRequest) => {
    try {
      const response = await apiClient.post<SuggestionResponse>("/content/suggestions", request);
      return response.data;
    } catch (error) {
      console.error("Error getting suggestions:", error);
      // For now, return mock data if the API endpoint doesn't exist yet
      return getMockSuggestions(request.suggestion_type);
    }
  },
};

// Mock data for development until the backend API is implemented
function getMockSuggestions(type: string): SuggestionResponse {
  const mockData: Record<string, Suggestion[]> = {
    improve: [
      {
        id: 'improve-1',
        text: 'Consider adding more specific examples to strengthen your point.',
        type: 'improve',
        description: 'Adding concrete examples makes your content more relatable and convincing.'
      },
      {
        id: 'improve-2',
        text: 'Your introduction could be more attention-grabbing. Try starting with a question or surprising fact.',
        type: 'improve',
        description: 'A strong hook increases engagement and readership.'
      }
    ],
    tone: [
      {
        id: 'tone-1',
        text: 'Your content could benefit from a more conversational tone to connect with readers.',
        type: 'tone',
        description: 'A conversational tone builds rapport with your audience.'
      },
      {
        id: 'tone-2',
        text: 'Consider using more authoritative language to establish expertise.',
        type: 'tone',
        description: 'Authoritative language builds credibility with your audience.'
      }
    ],
    hashtags: [
      {
        id: 'hashtag-1',
        text: '#AITrends #TechInnovation #FutureTech',
        type: 'hashtags',
        description: 'Popular hashtags in the tech industry'
      },
      {
        id: 'hashtag-2',
        text: '#MachineLearning #DataScience #ArtificialIntelligence',
        type: 'hashtags',
        description: 'Specific AI-related hashtags'
      }
    ],
    engagement: [
      {
        id: 'engagement-1',
        text: 'End with a question to encourage comments and discussion.',
        type: 'engagement',
        description: 'Questions prompt readers to engage with your content.'
      },
      {
        id: 'engagement-2',
        text: 'Include a call-to-action to guide readers on what to do next.',
        type: 'engagement',
        description: 'Clear CTAs improve conversion rates.'
      }
    ]
  };

  return {
    suggestions: mockData[type] || []
  };
}

export default aiSuggestionsService;
