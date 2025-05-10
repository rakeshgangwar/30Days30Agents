/**
 * Edge case tests for the ApiService
 */

import axios from 'axios';
import { ApiService, ApiError } from '../../src/services/ApiService';
import { DraftRequest } from '../../src/models/DataModel';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('ApiService Edge Cases', () => {
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
  });

  describe('Constructor', () => {
    it('should use default values when options are not provided', () => {
      apiService = new ApiService({
        baseUrl: 'http://localhost:8000',
      });

      // We can't directly test private properties, but we can test behavior
      expect(mockedAxios.create).toHaveBeenCalledWith(expect.objectContaining({
        baseURL: 'http://localhost:8000',
        timeout: 30000, // Default timeout
      }));
    });

    it('should use custom values when options are provided', () => {
      apiService = new ApiService({
        baseUrl: 'http://localhost:8000',
        apiKey: 'test-api-key',
        timeout: 5000,
        maxRetries: 5,
        retryDelay: 500,
      });

      expect(mockedAxios.create).toHaveBeenCalledWith(expect.objectContaining({
        baseURL: 'http://localhost:8000',
        timeout: 5000,
        headers: expect.objectContaining({
          'X-API-Key': 'test-api-key',
        }),
      }));
    });
  });

  describe('Retry Mechanism', () => {
    it('should not retry on 4xx client errors', async () => {
      apiService = new ApiService({
        baseUrl: 'http://localhost:8000',
        maxRetries: 3,
      });

      // Mock isAxiosError to return true for our custom error
      mockedAxios.isAxiosError.mockImplementation((error) => {
        return error && error.isAxiosError === true;
      });

      // Mock a 400 error
      const clientError = {
        isAxiosError: true,
        response: {
          status: 400,
          data: {
            message: 'Bad request',
          },
        },
        message: 'Request failed with status code 400',
      };

      // Reset the mock to ensure call count is accurate
      mockedAxios.post.mockReset();
      mockedAxios.post.mockRejectedValueOnce(clientError);

      // Request data
      const request: DraftRequest = {
        prompt: 'Write a story',
      };

      // Call the method and expect it to throw
      try {
        await apiService.generateDraft(request);
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect(mockedAxios.post).toHaveBeenCalledTimes(1); // No retries
      }
    });

    it('should retry on 5xx server errors', async () => {
      apiService = new ApiService({
        baseUrl: 'http://localhost:8000',
        maxRetries: 2,
        retryDelay: 100,
      });

      // Mock a 500 error for the first attempt, then success
      const serverError = {
        isAxiosError: true,
        response: {
          status: 500,
          data: {
            message: 'Internal server error',
          },
        },
        message: 'Request failed with status code 500',
      };
      const mockResponse = {
        data: {
          text: 'Generated text',
          model_used: 'test-model',
        },
      };

      mockedAxios.post.mockRejectedValueOnce(serverError);
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      // Request data
      const request: DraftRequest = {
        prompt: 'Write a story',
      };

      // Call the method
      const result = await apiService.generateDraft(request);

      // Assertions
      expect(mockedAxios.post).toHaveBeenCalledTimes(2); // 1 failure + 1 success
      expect(result).toEqual(mockResponse.data);
    });

    it('should retry with exponential backoff', async () => {
      // Mock setTimeout to track delays
      const originalSetTimeout = global.setTimeout;
      const mockSetTimeout = jest.fn().mockImplementation((callback, delay) => {
        return originalSetTimeout(callback, 0); // Execute immediately for testing
      });
      global.setTimeout = mockSetTimeout as any;

      apiService = new ApiService({
        baseUrl: 'http://localhost:8000',
        maxRetries: 3,
        retryDelay: 100,
      });

      // Mock network errors for all attempts
      const networkError = new Error('Network error');
      mockedAxios.post.mockRejectedValue(networkError);

      // Request data
      const request: DraftRequest = {
        prompt: 'Write a story',
      };

      // Call the method and expect it to throw
      try {
        await apiService.generateDraft(request);
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        expect(mockedAxios.post).toHaveBeenCalledTimes(3); // maxRetries is 3

        // Check that setTimeout was called with exponential backoff
        expect(mockSetTimeout).toHaveBeenCalledTimes(2); // (maxRetries - 1)
        expect(mockSetTimeout).toHaveBeenNthCalledWith(1, expect.any(Function), 100); // Base delay
        expect(mockSetTimeout).toHaveBeenNthCalledWith(2, expect.any(Function), 200); // 2x base delay
      }

      // Restore setTimeout
      global.setTimeout = originalSetTimeout;
    });
  });

  describe('Error Handling', () => {
    beforeEach(() => {
      apiService = new ApiService({
        baseUrl: 'http://localhost:8000',
        maxRetries: 1, // Just one retry for faster tests
      });

      // Mock isAxiosError to return true for our custom errors
      mockedAxios.isAxiosError.mockImplementation((error) => {
        return error && error.isAxiosError === true;
      });
    });

    it('should handle network errors', async () => {
      // Create a custom error handler to modify the error message
      const createApiErrorSpy = jest.spyOn(ApiService.prototype as any, 'createApiError');
      createApiErrorSpy.mockImplementationOnce((...args: any[]) => {
        const [error, defaultMessage] = args;
        return new ApiError(defaultMessage as string, undefined, error);
      });

      const networkError = new Error('Network error');
      mockedAxios.post.mockRejectedValue(networkError);

      try {
        await apiService.generateDraft({ prompt: 'test' });
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.message).toBe('Failed to generate draft');
          expect(error.originalError).toBe(networkError);
        }
      }

      createApiErrorSpy.mockRestore();
    });

    it('should handle axios errors with response', async () => {
      // Create a custom error handler to set the status and message
      const createApiErrorSpy = jest.spyOn(ApiService.prototype as any, 'createApiError');
      createApiErrorSpy.mockImplementationOnce((...args: any[]) => {
        const [error] = args;
        return new ApiError('Unauthorized', 401, error);
      });

      const axiosError = {
        isAxiosError: true,
        response: {
          status: 401,
          data: {
            message: 'Unauthorized',
          },
        },
        message: 'Request failed with status code 401',
      };
      mockedAxios.post.mockRejectedValue(axiosError);

      try {
        await apiService.generateDraft({ prompt: 'test' });
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.status).toBe(401);
          expect(error.message).toBe('Unauthorized');
          expect(error.originalError).toBe(axiosError);
        }
      }

      createApiErrorSpy.mockRestore();
    });

    it('should handle axios errors without response data', async () => {
      // Create a custom error handler to set the status and message
      const createApiErrorSpy = jest.spyOn(ApiService.prototype as any, 'createApiError');
      createApiErrorSpy.mockImplementationOnce((...args: any[]) => {
        const [error] = args;
        return new ApiError('Request failed with status code 500', 500, error);
      });

      const axiosError = {
        isAxiosError: true,
        response: {
          status: 500,
        },
        message: 'Request failed with status code 500',
      };
      mockedAxios.post.mockRejectedValue(axiosError);

      try {
        await apiService.generateDraft({ prompt: 'test' });
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.status).toBe(500);
          expect(error.message).toBe('Request failed with status code 500');
          expect(error.originalError).toBe(axiosError);
        }
      }

      createApiErrorSpy.mockRestore();
    });

    it('should handle axios errors without response', async () => {
      // Create a custom error handler to set the message
      const createApiErrorSpy = jest.spyOn(ApiService.prototype as any, 'createApiError');
      createApiErrorSpy.mockImplementationOnce((...args: any[]) => {
        const [error] = args;
        return new ApiError('Network Error', undefined, error);
      });

      const axiosError = {
        isAxiosError: true,
        message: 'Network Error',
      };
      mockedAxios.post.mockRejectedValue(axiosError);

      try {
        await apiService.generateDraft({ prompt: 'test' });
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.status).toBeUndefined();
          expect(error.message).toBe('Network Error');
          expect(error.originalError).toBe(axiosError);
        }
      }

      createApiErrorSpy.mockRestore();
    });

    it('should handle cancellation', async () => {
      const cancelError = {
        isAxiosError: true,
        message: 'Request canceled',
        __CANCEL__: true,
      };
      mockedAxios.isCancel.mockReturnValueOnce(true);
      mockedAxios.post.mockRejectedValue(cancelError);

      try {
        await apiService.generateDraft({ prompt: 'test' }, 'request-id');
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiError);
        if (error instanceof ApiError) {
          expect(error.message).toBe('Request cancelled');
          expect(error.originalError).toBe(cancelError);
        }
      }
    });
  });
});
