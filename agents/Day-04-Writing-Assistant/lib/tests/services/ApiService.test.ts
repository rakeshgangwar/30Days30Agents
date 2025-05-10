import axios from 'axios';
import { ApiService, ApiError } from '../../src/services/ApiService';
import {
  DraftRequest,
  AnalyzeGrammarStyleRequest,
  SummarizeRequest,
  AdjustToneRequest,
  UserPreferences,
} from '../../src/models/DataModel';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ApiService', () => {
  let apiService: ApiService;
  const mockBaseUrl = 'http://localhost:8000';
  const mockApiKey = 'test-api-key';
  const mockCancelToken = { token: 'mock-token' };

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Mock axios.create to return mockedAxios
    mockedAxios.create.mockReturnValue(mockedAxios as any);

    // Mock axios.CancelToken.source
    mockedAxios.CancelToken = {
      source: jest.fn().mockReturnValue({
        token: mockCancelToken,
        cancel: jest.fn(),
      }),
    } as any;

    // Create a new ApiService instance before each test
    apiService = new ApiService({
      baseUrl: mockBaseUrl,
      apiKey: mockApiKey,
      maxRetries: 2,
      retryDelay: 100,
    });
  });

  describe('checkHealth', () => {
    it('should return true when the API is available', async () => {
      mockedAxios.get.mockResolvedValueOnce({ status: 200 });

      const result = await apiService.checkHealth();

      expect(result).toBe(true);
      expect(mockedAxios.get).toHaveBeenCalledWith('/health');
    });

    it('should return false when the API is unavailable', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));

      const result = await apiService.checkHealth();

      expect(result).toBe(false);
      expect(mockedAxios.get).toHaveBeenCalledWith('/health');
    });
  });

  describe('generateDraft', () => {
    it('should call the /api/v1/draft endpoint with the correct parameters', async () => {
      // Mock response
      const mockResponse = {
        data: {
          text: 'Generated draft text',
          model_used: 'test-model',
        },
      };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      // Request data
      const request: DraftRequest = {
        prompt: 'Write a short story about a robot',
        max_length: 500,
      };

      // Call the method
      const result = await apiService.generateDraft(request);

      // Assertions
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/draft', request, { cancelToken: undefined });
      expect(result).toEqual(mockResponse.data);
    });

    it('should use a cancel token when requestId is provided', async () => {
      // Mock response
      const mockResponse = {
        data: {
          text: 'Generated draft text',
          model_used: 'test-model',
        },
      };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      // Request data
      const request: DraftRequest = {
        prompt: 'Write a short story about a robot',
      };

      // Call the method with a requestId
      const result = await apiService.generateDraft(request, 'test-request-id');

      // Assertions
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/draft', request, { cancelToken: mockCancelToken });
      expect(result).toEqual(mockResponse.data);
    });

    it('should retry on network errors', async () => {
      // Mock error for first attempt, success for second attempt
      const mockError = new Error('Network error');
      const mockResponse = {
        data: {
          text: 'Generated draft text',
          model_used: 'test-model',
        },
      };

      mockedAxios.post.mockRejectedValueOnce(mockError);
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      // Request data
      const request: DraftRequest = {
        prompt: 'Write a short story about a robot',
      };

      // Call the method
      const result = await apiService.generateDraft(request);

      // Assertions
      expect(mockedAxios.post).toHaveBeenCalledTimes(2);
      expect(result).toEqual(mockResponse.data);
    });

    it('should throw ApiError after all retries fail', async () => {
      // Mock error for all attempts
      const mockError = new Error('Network error');
      mockedAxios.post.mockRejectedValue(mockError);

      // Request data
      const request: DraftRequest = {
        prompt: 'Write a short story about a robot',
      };

      // Call the method and expect it to throw
      await expect(apiService.generateDraft(request)).rejects.toBeInstanceOf(ApiError);
      expect(mockedAxios.post).toHaveBeenCalledTimes(2); // maxRetries is 2
    });
  });

  describe('analyzeGrammarStyle', () => {
    it('should call the /api/v1/analyze_grammar_style endpoint with the correct parameters', async () => {
      // Mock response
      const mockResponse = {
        data: {
          issues: [],
          improved_text: 'Improved text',
          model_used: 'test-model',
        },
      };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      // Request data
      const request: AnalyzeGrammarStyleRequest = {
        text: 'Text to analyze',
        checks: ['grammar', 'style'],
      };

      // Call the method
      const result = await apiService.analyzeGrammarStyle(request);

      // Assertions
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/analyze_grammar_style', request, { cancelToken: undefined });
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('summarize', () => {
    it('should call the /api/v1/summarize endpoint with the correct parameters', async () => {
      // Mock response
      const mockResponse = {
        data: {
          summary: 'Summarized text',
          model_used: 'test-model',
        },
      };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      // Request data
      const request: SummarizeRequest = {
        text: 'Text to summarize',
        max_length: 100,
      };

      // Call the method
      const result = await apiService.summarize(request);

      // Assertions
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/summarize', request, { cancelToken: undefined });
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('adjustTone', () => {
    it('should call the /api/v1/adjust_tone endpoint with the correct parameters', async () => {
      // Mock response
      const mockResponse = {
        data: {
          original_text: 'Original text',
          adjusted_text: 'Adjusted text',
          target_tone: 'professional',
          model_used: 'test-model',
        },
      };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      // Request data
      const request: AdjustToneRequest = {
        text: 'Text to adjust',
        target_tone: 'professional',
      };

      // Call the method
      const result = await apiService.adjustTone(request);

      // Assertions
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/adjust_tone', request, { cancelToken: undefined });
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('getUserPreferences', () => {
    it('should call the /api/v1/preferences/{userId} endpoint with the correct parameters', async () => {
      // Mock response
      const mockResponse = {
        data: {
          preferred_model: 'test-model',
          default_tone: 'professional',
        },
      };
      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      // Call the method
      const result = await apiService.getUserPreferences('user123');

      // Assertions
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/preferences/user123', { cancelToken: undefined });
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('updateUserPreferences', () => {
    it('should call the /api/v1/preferences/{userId} endpoint with the correct parameters', async () => {
      // Mock response
      const mockResponse = {
        data: {
          preferred_model: 'updated-model',
          default_tone: 'casual',
        },
      };
      mockedAxios.put.mockResolvedValueOnce(mockResponse);

      // Request data
      const preferences: UserPreferences = {
        preferred_model: 'updated-model',
        default_tone: 'casual',
      };

      // Call the method
      const result = await apiService.updateUserPreferences('user123', preferences);

      // Assertions
      expect(mockedAxios.put).toHaveBeenCalledWith('/api/v1/preferences/user123', preferences, { cancelToken: undefined });
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('cancelRequest', () => {
    it('should cancel an ongoing request', async () => {
      // Setup
      const requestId = 'test-request-id';
      const cancelMock = jest.fn();

      // Mock the cancel token source
      (mockedAxios.CancelToken.source as jest.Mock).mockReturnValueOnce({
        token: mockCancelToken,
        cancel: cancelMock,
      });

      // Make a request with the requestId to store the cancel token source
      mockedAxios.post.mockResolvedValueOnce({ data: {} });
      await apiService.generateDraft({ prompt: 'test' }, requestId);

      // Cancel the request
      apiService.cancelRequest(requestId);

      // Assertions
      expect(cancelMock).toHaveBeenCalledWith('Request cancelled by user');
    });

    it('should do nothing if the requestId does not exist', () => {
      // Cancel a non-existent request
      apiService.cancelRequest('non-existent-id');

      // No assertions needed, just make sure it doesn't throw
    });
  });
});
