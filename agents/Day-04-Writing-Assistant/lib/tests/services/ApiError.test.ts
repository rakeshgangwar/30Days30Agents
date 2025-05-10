/**
 * Tests for the ApiError class
 */

import { ApiError } from '../../src/services/ApiService';
import axios from 'axios';

describe('ApiError', () => {
  it('should create an instance with a message', () => {
    const error = new ApiError('Test error message');
    
    expect(error).toBeInstanceOf(Error);
    expect(error).toBeInstanceOf(ApiError);
    expect(error.message).toBe('Test error message');
    expect(error.name).toBe('ApiError');
    expect(error.status).toBeUndefined();
    expect(error.originalError).toBeUndefined();
  });
  
  it('should create an instance with a message and status', () => {
    const error = new ApiError('Test error message', 404);
    
    expect(error.message).toBe('Test error message');
    expect(error.status).toBe(404);
    expect(error.originalError).toBeUndefined();
  });
  
  it('should create an instance with a message, status, and original error', () => {
    const originalError = new Error('Original error');
    const error = new ApiError('Test error message', 500, originalError);
    
    expect(error.message).toBe('Test error message');
    expect(error.status).toBe(500);
    expect(error.originalError).toBe(originalError);
  });
  
  it('should work with axios errors', () => {
    const axiosError = {
      isAxiosError: true,
      response: {
        status: 429,
        data: {
          message: 'Rate limit exceeded',
        },
      },
      message: 'Request failed with status code 429',
    };
    
    const error = new ApiError('API rate limit exceeded', 429, axiosError);
    
    expect(error.message).toBe('API rate limit exceeded');
    expect(error.status).toBe(429);
    expect(error.originalError).toBe(axiosError);
  });
  
  it('should be throwable and catchable', () => {
    const throwError = () => {
      throw new ApiError('Test error', 400);
    };
    
    expect(throwError).toThrow(ApiError);
    expect(throwError).toThrow('Test error');
    
    try {
      throwError();
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      if (error instanceof ApiError) {
        expect(error.status).toBe(400);
      }
    }
  });
});
