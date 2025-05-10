/**
 * API Service for the Writing Assistant
 *
 * This service provides methods to interact with the Writing Assistant API endpoints.
 * It handles authentication, error handling, and provides a clean interface for
 * making requests to the backend.
 */

import axios, { AxiosInstance, AxiosRequestConfig, CancelTokenSource } from 'axios';
import {
  DraftRequest,
  DraftResponse,
  AnalyzeGrammarStyleRequest,
  AnalyzeGrammarStyleResponse,
  SummarizeRequest,
  SummarizeResponse,
  AdjustToneRequest,
  AdjustToneResponse,
  UserPreferences,
} from '../models/DataModel';

/**
 * Configuration options for the API service
 */
export interface ApiServiceConfig {
  /** Base URL of the Writing Assistant API (e.g., http://localhost:8000) */
  baseUrl: string;
  /** Optional API key for authentication */
  apiKey?: string;
  /** Request timeout in milliseconds (default: 30000) */
  timeout?: number;
  /** Maximum number of retry attempts for failed requests (default: 3) */
  maxRetries?: number;
  /** Delay between retries in milliseconds (default: 1000) */
  retryDelay?: number;
}

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  /** HTTP status code */
  status?: number;
  /** Original error object */
  originalError: any;

  constructor(message: string, status?: number, originalError?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.originalError = originalError;
  }
}

/**
 * API Service for interacting with the Writing Assistant backend
 */
export class ApiService {
  private client: AxiosInstance;
  private cancelTokenSources: Map<string, CancelTokenSource> = new Map();
  private maxRetries: number;
  private retryDelay: number;

  /**
   * Create a new API service instance
   * @param config Configuration options
   */
  constructor(config: ApiServiceConfig) {
    this.maxRetries = config.maxRetries || 3;
    this.retryDelay = config.retryDelay || 1000;

    const axiosConfig: AxiosRequestConfig = {
      baseURL: config.baseUrl,
      timeout: config.timeout || 30000, // Default timeout: 30 seconds
      headers: {
        'Content-Type': 'application/json',
      },
    };

    // Add API key if provided
    if (config.apiKey) {
      axiosConfig.headers = {
        ...axiosConfig.headers,
        'X-API-Key': config.apiKey,
      };
    }

    this.client = axios.create(axiosConfig);
  }

  /**
   * Check if the API is available
   * @returns True if the API is available
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }

  /**
   * Generate a draft based on a prompt
   * @param request Draft request parameters
   * @param requestId Optional identifier for the request (for cancellation)
   * @returns Generated draft text
   * @throws {ApiError} If the request fails
   */
  async generateDraft(request: DraftRequest, requestId?: string): Promise<DraftResponse> {
    return this.executeWithRetry<DraftResponse>(
      async () => {
        const cancelToken = this.getCancelToken(requestId);
        const response = await this.client.post<DraftResponse>(
          '/api/v1/draft',
          request,
          { cancelToken }
        );
        return response.data;
      },
      'Failed to generate draft'
    );
  }

  /**
   * Analyze text for grammar and style issues
   * @param request Analysis request parameters
   * @param requestId Optional identifier for the request (for cancellation)
   * @returns Analysis results with issues and improved text
   * @throws {ApiError} If the request fails
   */
  async analyzeGrammarStyle(
    request: AnalyzeGrammarStyleRequest,
    requestId?: string
  ): Promise<AnalyzeGrammarStyleResponse> {
    return this.executeWithRetry<AnalyzeGrammarStyleResponse>(
      async () => {
        const cancelToken = this.getCancelToken(requestId);
        const response = await this.client.post<AnalyzeGrammarStyleResponse>(
          '/api/v1/analyze_grammar_style',
          request,
          { cancelToken }
        );
        return response.data;
      },
      'Failed to analyze grammar and style'
    );
  }

  /**
   * Summarize text
   * @param request Summarize request parameters
   * @param requestId Optional identifier for the request (for cancellation)
   * @returns Summarized text
   * @throws {ApiError} If the request fails
   */
  async summarize(request: SummarizeRequest, requestId?: string): Promise<SummarizeResponse> {
    return this.executeWithRetry<SummarizeResponse>(
      async () => {
        const cancelToken = this.getCancelToken(requestId);
        const response = await this.client.post<SummarizeResponse>(
          '/api/v1/summarize',
          request,
          { cancelToken }
        );
        return response.data;
      },
      'Failed to summarize text'
    );
  }

  /**
   * Adjust the tone of text
   * @param request Tone adjustment request parameters
   * @param requestId Optional identifier for the request (for cancellation)
   * @returns Text with adjusted tone
   * @throws {ApiError} If the request fails
   */
  async adjustTone(request: AdjustToneRequest, requestId?: string): Promise<AdjustToneResponse> {
    return this.executeWithRetry<AdjustToneResponse>(
      async () => {
        const cancelToken = this.getCancelToken(requestId);
        const response = await this.client.post<AdjustToneResponse>(
          '/api/v1/adjust_tone',
          request,
          { cancelToken }
        );
        return response.data;
      },
      'Failed to adjust tone'
    );
  }

  /**
   * Get user preferences
   * @param userId User ID
   * @param requestId Optional identifier for the request (for cancellation)
   * @returns User preferences
   * @throws {ApiError} If the request fails
   */
  async getUserPreferences(userId: string, requestId?: string): Promise<UserPreferences> {
    return this.executeWithRetry<UserPreferences>(
      async () => {
        const cancelToken = this.getCancelToken(requestId);
        const response = await this.client.get<UserPreferences>(
          `/api/v1/preferences/${userId}`,
          { cancelToken }
        );
        return response.data;
      },
      'Failed to get user preferences'
    );
  }

  /**
   * Update user preferences
   * @param userId User ID
   * @param preferences User preferences to update
   * @param requestId Optional identifier for the request (for cancellation)
   * @returns Updated user preferences
   * @throws {ApiError} If the request fails
   */
  async updateUserPreferences(
    userId: string,
    preferences: UserPreferences,
    requestId?: string
  ): Promise<UserPreferences> {
    return this.executeWithRetry<UserPreferences>(
      async () => {
        const cancelToken = this.getCancelToken(requestId);
        const response = await this.client.put<UserPreferences>(
          `/api/v1/preferences/${userId}`,
          preferences,
          { cancelToken }
        );
        return response.data;
      },
      'Failed to update user preferences'
    );
  }

  /**
   * Cancel an ongoing request
   * @param requestId The ID of the request to cancel
   */
  cancelRequest(requestId: string): void {
    const source = this.cancelTokenSources.get(requestId);
    if (source) {
      source.cancel('Request cancelled by user');
      this.cancelTokenSources.delete(requestId);
    }
  }

  /**
   * Get a cancel token for a request
   * @param requestId Optional request ID
   * @returns Cancel token or undefined if no requestId provided
   */
  private getCancelToken(requestId?: string) {
    if (!requestId) return undefined;

    // Cancel any existing request with the same ID
    this.cancelRequest(requestId);

    // Create a new cancel token source
    const source = axios.CancelToken.source();
    this.cancelTokenSources.set(requestId, source);

    return source.token;
  }

  /**
   * Execute a function with retry logic
   * @param fn Function to execute
   * @param errorMessage Error message to use if the function fails
   * @returns Result of the function
   * @throws {ApiError} If the function fails after all retries
   */
  private async executeWithRetry<T>(
    fn: () => Promise<T>,
    errorMessage: string
  ): Promise<T> {
    let lastError: unknown;

    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error: unknown) {
        lastError = error;

        // Don't retry if the request was cancelled or if it's a client error (4xx)
        if (axios.isCancel(error)) {
          throw new ApiError('Request cancelled', undefined, error);
        }

        // Type guard for Axios errors
        const isAxiosError = (err: unknown): err is { response?: { status: number } } => {
          return axios.isAxiosError(err);
        };

        if (isAxiosError(error) && error.response && error.response.status >= 400 && error.response.status < 500) {
          break;
        }

        // Wait before retrying (exponential backoff)
        if (attempt < this.maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, this.retryDelay * Math.pow(2, attempt)));
        }
      }
    }

    // If we get here, all retries failed
    throw this.createApiError(lastError, errorMessage);
  }

  /**
   * Create an ApiError from an error object
   * @param error Error object
   * @param defaultMessage Default error message
   * @returns ApiError
   */
  private createApiError(error: unknown, defaultMessage: string): ApiError {
    // Type guard for Axios errors
    const isAxiosError = (err: unknown): err is {
      response?: {
        status?: number;
        data?: {
          message?: string;
        };
      };
      message?: string;
    } => {
      return axios.isAxiosError(err);
    };

    if (isAxiosError(error)) {
      const status = error.response?.status;
      const message = error.response?.data?.message || error.message || defaultMessage;

      return new ApiError(message, status, error);
    }

    // For non-Axios errors, try to extract a message if it's an Error object
    if (error instanceof Error) {
      return new ApiError(error.message || defaultMessage, undefined, error);
    }

    return new ApiError(defaultMessage, undefined, error);
  }
}
