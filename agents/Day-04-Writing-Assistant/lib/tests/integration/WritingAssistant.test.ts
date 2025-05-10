/**
 * Integration tests for the Writing Assistant connector library
 *
 * These tests simulate real-world usage of the library by combining
 * multiple components together.
 */

import axios from 'axios';
import {
  ApiService,
  ApiError,
  RequestFactory,
  ResponseUtils,
  LLMModel,
  TextTone,
  SummaryFormat,
  CheckType,
} from '../../src';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Writing Assistant Integration Tests', () => {
  let apiService: ApiService;

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Mock axios.create to return mockedAxios
    mockedAxios.create.mockReturnValue(mockedAxios as any);

    // Mock axios.CancelToken.source
    mockedAxios.CancelToken = {
      source: jest.fn().mockReturnValue({
        token: 'mock-token',
        cancel: jest.fn(),
      }),
    } as any;

    // Create a new ApiService instance before each test
    apiService = new ApiService({
      baseUrl: 'http://localhost:8000',
      apiKey: 'test-api-key',
    });
  });

  describe('Draft Generation Workflow', () => {
    it('should generate a draft and handle the response', async () => {
      // Mock response
      const mockResponse = {
        data: {
          text: 'Generated draft text about robots in a science fiction setting.',
          model_used: LLMModel.CLAUDE_HAIKU,
        },
      };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      // Create a request using the factory
      const request = RequestFactory.createDraftRequest(
        'Write a short story about a robot',
        {
          context: 'Science fiction setting',
          max_length: 500,
          model: LLMModel.CLAUDE_HAIKU,
          temperature: 0.7,
        }
      );

      // Generate the draft
      const result = await apiService.generateDraft(request);

      // Assertions
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/v1/draft',
        request,
        { cancelToken: undefined }
      );
      expect(result).toEqual(mockResponse.data);
      expect(result.text).toContain('robots');
      expect(result.model_used).toBe(LLMModel.CLAUDE_HAIKU);
    });
  });

  describe('Grammar Analysis Workflow', () => {
    it('should analyze text and process the results', async () => {
      // Mock response
      const mockResponse = {
        data: {
          issues: [
            {
              type: CheckType.GRAMMAR,
              description: 'Subject-verb agreement error',
              suggestion: 'Change "is" to "are"',
              severity: 'high'
            },
            {
              type: CheckType.STYLE,
              description: 'Passive voice',
              suggestion: 'Use active voice',
              severity: 'medium'
            },
            {
              type: CheckType.SPELLING,
              description: 'Misspelled word',
              suggestion: 'Change "teh" to "the"',
              severity: 'low'
            },
          ],
          improved_text: 'This is the improved text with corrections.',
          model_used: LLMModel.GPT_4,
        },
      };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      // Create a request using the factory
      const request = RequestFactory.createAnalyzeGrammarStyleRequest(
        'This is teh text with some grammar errors.',
        {
          checks: [CheckType.GRAMMAR, CheckType.STYLE, CheckType.SPELLING],
          check_grammar: true,
          check_style: true,
          check_spelling: true,
        }
      );

      // Analyze the text
      const result = await apiService.analyzeGrammarStyle(request);

      // Get important issues
      const importantIssues = ResponseUtils.getImportantIssues(result, 2);

      // Calculate improvement percentage
      const improvementPercentage = ResponseUtils.calculateImprovementPercentage(result);

      // Assertions
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/v1/analyze_grammar_style',
        request,
        { cancelToken: undefined }
      );
      expect(result).toEqual(mockResponse.data);
      expect(importantIssues).toHaveLength(2);
      expect(importantIssues[0].type).toBe(CheckType.GRAMMAR);
      expect(importantIssues[1].type).toBe(CheckType.STYLE);
      expect(improvementPercentage).toBeGreaterThan(0);
    });
  });

  describe('Summarization Workflow', () => {
    it('should summarize text and format the results', async () => {
      // Mock response
      const mockResponse = {
        data: {
          summary: 'First key point. Second key point. Third key point.',
          model_used: LLMModel.CLAUDE_HAIKU,
          original_length: 1000,
          summary_length: 100,
        },
      };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      // Create a request using the factory
      const request = RequestFactory.createSummarizeRequest(
        'This is a long text that needs to be summarized...',
        {
          max_length: 100,
          format: SummaryFormat.PARAGRAPH,
        }
      );

      // Summarize the text
      const result = await apiService.summarize(request);

      // Format as bullet points
      const bulletPoints = ResponseUtils.formatSummary(
        result.summary,
        SummaryFormat.BULLETS
      );

      // Assertions
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/v1/summarize',
        request,
        { cancelToken: undefined }
      );
      expect(result).toEqual(mockResponse.data);
      expect(bulletPoints).toContain('• First key point');
      expect(bulletPoints).toContain('• Second key point');
      expect(bulletPoints).toContain('• Third key point');
      expect(bulletPoints.split('\n')).toHaveLength(3);
    });
  });

  describe('Tone Adjustment Workflow', () => {
    it('should adjust the tone of text', async () => {
      // Mock response
      const mockResponse = {
        data: {
          original_text: "Hey dude, what's up with that report?",
          adjusted_text: "Hello, I was wondering about the status of the report.",
          target_tone: TextTone.PROFESSIONAL,
          model_used: LLMModel.GPT_4,
        },
      };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      // Create a request using the factory
      const request = RequestFactory.createAdjustToneRequest(
        "Hey dude, what's up with that report?",
        TextTone.PROFESSIONAL,
        {
          preserve_meaning: true,
          strength: 0.8,
        }
      );

      // Adjust the tone
      const result = await apiService.adjustTone(request);

      // Assertions
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/v1/adjust_tone',
        request,
        { cancelToken: undefined }
      );
      expect(result).toEqual(mockResponse.data);
      expect(result.adjusted_text).toContain('Hello');
      expect(result.target_tone).toBe(TextTone.PROFESSIONAL);
    });
  });

  describe('Error Handling Workflow', () => {
    it('should handle API errors properly', async () => {
      // Mock isAxiosError to return true for our custom error
      mockedAxios.isAxiosError.mockImplementation((error) => {
        return error && error.isAxiosError === true;
      });

      // Create a custom error handler to set the status and message
      const createApiErrorSpy = jest.spyOn(ApiService.prototype as any, 'createApiError');
      createApiErrorSpy.mockImplementationOnce((...args: any[]) => {
        const [error] = args;
        return new ApiError('Invalid request: prompt is required', 400, error);
      });

      // Mock error response
      const errorResponse = {
        isAxiosError: true,
        response: {
          status: 400,
          data: {
            message: 'Invalid request: prompt is required',
          },
        },
      };
      mockedAxios.post.mockRejectedValueOnce(errorResponse);

      // Create an invalid request (we'll bypass the factory validation)
      const request = {
        // Missing prompt field
        max_length: 500,
      } as any;

      // Try to generate a draft
      try {
        await apiService.generateDraft(request);
        fail('Should have thrown an error');
      } catch (error) {
        // Assertions
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.status).toBe(400);
          expect(error.message).toContain('Invalid request');
        }
      }

      createApiErrorSpy.mockRestore();
    });
  });

  describe('Cancellation Workflow', () => {
    // Increase the timeout for this test
    it('should cancel an ongoing request', async () => {
      // Setup
      const requestId = 'draft-request-1';
      const cancelMock = jest.fn();

      // Mock isAxiosError and isCancel
      mockedAxios.isAxiosError.mockImplementation(() => false);
      mockedAxios.isCancel.mockImplementation(() => true);

      // Mock the cancel token source
      (mockedAxios.CancelToken.source as jest.Mock).mockReturnValueOnce({
        token: 'mock-token',
        cancel: cancelMock,
      });

      // Create a custom error handler for cancellation
      const createApiErrorSpy = jest.spyOn(ApiService.prototype as any, 'createApiError');
      createApiErrorSpy.mockImplementationOnce((...args: any[]) => {
        return new ApiError('Request cancelled', undefined, { __CANCEL__: true });
      });

      // Mock axios to immediately reject with a cancellation error
      const cancelError = { __CANCEL__: true };
      mockedAxios.post.mockRejectedValueOnce(cancelError);

      // Start the request
      const requestPromise = apiService.generateDraft(
        RequestFactory.createDraftRequest('Write a story'),
        requestId
      );

      // Cancel the request
      apiService.cancelRequest(requestId);

      // Assertions
      expect(cancelMock).toHaveBeenCalledWith('Request cancelled by user');

      // The request should be rejected with a cancellation error
      await expect(requestPromise).rejects.toThrow('Request cancelled');

      createApiErrorSpy.mockRestore();
    }, 10000); // Increase timeout to 10 seconds
  });
});
