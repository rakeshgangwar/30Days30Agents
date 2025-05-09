# OpenAI Integration

This document provides details about the implementation of the OpenAI integration in the Code Assistant project.

## Table of Contents

1. [Overview](#overview)
2. [Implementation Details](#implementation-details)
3. [Usage](#usage)
4. [Error Handling](#error-handling)
5. [Future Improvements](#future-improvements)

## Overview

The OpenAI integration is a critical component of the Code Assistant, enabling AI-powered code analysis. It uses the OpenAI API to analyze code files and repositories, identifying potential issues, improvements, and best practices.

## Implementation Details

The OpenAI integration is implemented in the `AIAnalysisCoordinator` component, specifically in the `AIInteractor` class. It uses the latest OpenAI Node.js SDK (v4.x) to interact with the OpenAI API.

### Key Components

#### AIInteractor Class

The `AIInteractor` class handles API calls to OpenAI:

```javascript
class AIInteractor {
  constructor(config = {}) {
    this.config = {
      provider: config.provider || 'openai',
      model: config.model || 'gpt-4',
      temperature: config.temperature !== undefined ? config.temperature : 0.2,
      maxTokens: config.maxTokens || 2000,
      ...config
    };

    this.openaiApi = null;

    // Initialize AI provider
    if (this.config.provider === 'openai' && config.openai && config.openai.apiKey) {
      this.initializeOpenAI(config.openai);
    }
  }

  initializeOpenAI(config) {
    try {
      this.openaiApi = new OpenAI({
        apiKey: config.apiKey
      });
      this.openaiInitialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize OpenAI client:', error.message);
      this.openaiInitialized = false;
      return false;
    }
  }

  async analyzeWithAI(prompt, options = {}) {
    if (!this.openaiInitialized || !this.openaiApi) {
      console.warn('OpenAI client not initialized, using mock response');
      return this.createMockResponse(prompt);
    }

    try {
      // Set up request parameters
      const requestOptions = {
        model: options.model || this.config.model,
        messages: [
          { role: 'system', content: 'You are a code analysis assistant that provides detailed, accurate analysis of code and repositories.' },
          { role: 'user', content: prompt }
        ],
        temperature: options.temperature !== undefined ? options.temperature : this.config.temperature,
        max_tokens: options.maxTokens || this.config.maxTokens,
        top_p: 1,
        frequency_penalty: 0,
        presence_penalty: 0
      };

      // Call OpenAI API
      console.log(`Calling OpenAI API with model: ${requestOptions.model}`);
      const response = await this.openaiApi.chat.completions.create(requestOptions);

      // Extract and return the response content
      if (response &&
          response.choices &&
          response.choices.length > 0 &&
          response.choices[0].message) {
        return {
          success: true,
          response: response.choices[0].message.content,
          usage: response.usage
        };
      } else {
        throw new Error('Invalid response format from OpenAI API');
      }
    } catch (error) {
      console.error('Error calling OpenAI API:', error.message);

      // Fall back to mock response in case of error
      console.warn('Using mock response as fallback');
      return this.createMockResponse(prompt);
    }
  }
}
```

### Key Features

- **Initialization**: The OpenAI client is initialized with the provided API key
- **Configuration**: Supports configuration of model, temperature, and token limits
- **Error Handling**: Includes robust error handling with fallback to mock responses
- **Mock Responses**: Provides mock responses when the API is unavailable or for testing

## Usage

The OpenAI integration is used by the `AIAnalysisCoordinator` to analyze code files and repositories:

```javascript
// Initialize the coordinator
const coordinator = new AIAnalysisCoordinator({
  provider: 'openai',
  model: 'gpt-4',
  openai: {
    apiKey: process.env.OPENAI_API_KEY
  }
});

// Analyze a file
const fileAnalysisResult = await coordinator.analyzeFile(file, codeAnalysisResult);

// Analyze a repository
const repoAnalysisResult = await coordinator.analyzeRepository(repositoryInfo, analysisResults);
```

## Error Handling

The OpenAI integration includes robust error handling:

1. **Initialization Errors**: If the OpenAI client fails to initialize, the error is logged and the system falls back to mock responses
2. **API Call Errors**: If an API call fails, the error is logged and the system falls back to mock responses
3. **Response Validation**: The response is validated to ensure it contains the expected data structure

## Future Improvements

Future improvements to the OpenAI integration could include:

1. **Token Management**: Implement token counting to monitor usage and prevent exceeding limits
2. **Streaming Responses**: Support streaming responses for better user experience
3. **Function Calling**: Implement function calling for more structured responses
4. **Model Selection**: Support for selecting different models based on the task
5. **Rate Limiting**: Implement rate limiting and backoff strategies
6. **Caching**: Cache responses to reduce API calls and costs
