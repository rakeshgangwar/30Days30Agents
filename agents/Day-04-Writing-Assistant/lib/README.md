# Writing Assistant Connector Library

This library provides a shared interface for connectors (VS Code extension, Obsidian plugin, etc.) to interact with the Writing Assistant backend.

## Installation

```bash
npm install writing-assistant-connector
```

## Usage

### Initialize the API Service

```typescript
import { ApiService } from 'writing-assistant-connector';

const apiService = new ApiService({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your-api-key', // Optional
  timeout: 30000, // Optional, default: 30000 (30 seconds)
  maxRetries: 3, // Optional, default: 3
  retryDelay: 1000, // Optional, default: 1000 (1 second)
});

// Check if the API is available
const isAvailable = await apiService.checkHealth();
console.log('API available:', isAvailable);
```

### Generate a Draft

```typescript
import {
  ApiService,
  ApiError,
  DraftRequest,
  RequestFactory,
  LLMModel
} from 'writing-assistant-connector';

const apiService = new ApiService({
  baseUrl: 'http://localhost:8000',
});

// Using the RequestFactory for validation
const request = RequestFactory.createDraftRequest(
  'Write a short story about a robot',
  {
    max_length: 500,
    model: LLMModel.CLAUDE_HAIKU,
    temperature: 0.7,
  }
);

// Or create the request directly
const manualRequest: DraftRequest = {
  prompt: 'Write a short story about a robot',
  max_length: 500,
  model: LLMModel.CLAUDE_HAIKU,
  temperature: 0.7,
};

async function generateDraft() {
  try {
    // You can provide a requestId to enable cancellation
    const requestId = 'draft-1';
    const response = await apiService.generateDraft(request, requestId);
    console.log('Generated text:', response.text);
    console.log('Model used:', response.model_used);
  } catch (error) {
    if (error instanceof ApiError) {
      console.error(`API Error (${error.status}): ${error.message}`);
    } else {
      console.error('Failed to generate draft:', error);
    }
  }
}

// Cancel a request if needed
apiService.cancelRequest('draft-1');
```

### Analyze Grammar and Style

```typescript
import {
  ApiService,
  AnalyzeGrammarStyleRequest,
  RequestFactory,
  ResponseUtils,
  CheckType
} from 'writing-assistant-connector';

const apiService = new ApiService({
  baseUrl: 'http://localhost:8000',
});

// Using the RequestFactory for validation
const request = RequestFactory.createAnalyzeGrammarStyleRequest(
  'This is a text with some grammar errors and stylistic issues.',
  {
    checks: [CheckType.GRAMMAR, CheckType.STYLE, CheckType.CLARITY],
    check_grammar: true,
    check_style: true,
    check_spelling: false,
  }
);

async function analyzeText() {
  try {
    const response = await apiService.analyzeGrammarStyle(request);

    // Get the most important issues (sorted by severity)
    const importantIssues = ResponseUtils.getImportantIssues(response, 3);
    console.log('Top issues:', importantIssues);

    // Calculate improvement percentage
    const improvementPercentage = ResponseUtils.calculateImprovementPercentage(response);
    console.log(`Text improved by approximately ${improvementPercentage}%`);

    console.log('All issues:', response.issues);
    console.log('Improved text:', response.improved_text);
  } catch (error) {
    if (error instanceof ApiError) {
      console.error(`API Error (${error.status}): ${error.message}`);
    } else {
      console.error('Failed to analyze text:', error);
    }
  }
}
```

### Summarize Text

```typescript
import {
  ApiService,
  SummarizeRequest,
  RequestFactory,
  ResponseUtils,
  SummaryFormat
} from 'writing-assistant-connector';

const apiService = new ApiService({
  baseUrl: 'http://localhost:8000',
});

const request = RequestFactory.createSummarizeRequest(
  'Long text to summarize...',
  {
    max_length: 200,
    format: SummaryFormat.BULLETS,
    focus: 'main points',
  }
);

async function summarizeText() {
  try {
    const response = await apiService.summarize(request);

    // Format the summary if needed
    const formattedSummary = ResponseUtils.formatSummary(
      response.summary,
      SummaryFormat.PARAGRAPH
    );

    console.log('Original summary:', response.summary);
    console.log('Formatted summary:', formattedSummary);
    console.log('Summary length:', response.summary_length);
  } catch (error) {
    if (error instanceof ApiError) {
      console.error(`API Error (${error.status}): ${error.message}`);
    } else {
      console.error('Failed to summarize text:', error);
    }
  }
}
```

### Adjust Tone

```typescript
import {
  ApiService,
  AdjustToneRequest,
  RequestFactory,
  TextTone
} from 'writing-assistant-connector';

const apiService = new ApiService({
  baseUrl: 'http://localhost:8000',
});

const request = RequestFactory.createAdjustToneRequest(
  'Text to adjust tone...',
  TextTone.PROFESSIONAL,
  {
    preserve_meaning: true,
    strength: 0.8,
  }
);

async function adjustTone() {
  try {
    const response = await apiService.adjustTone(request);
    console.log('Adjusted text:', response.adjusted_text);
  } catch (error) {
    if (error instanceof ApiError) {
      console.error(`API Error (${error.status}): ${error.message}`);
    } else {
      console.error('Failed to adjust tone:', error);
    }
  }
}
```

### User Preferences

```typescript
import { ApiService, UserPreferences } from 'writing-assistant-connector';

const apiService = new ApiService({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your-api-key', // Required for user preferences
});

// Get user preferences
async function getUserPreferences(userId: string) {
  try {
    const preferences = await apiService.getUserPreferences(userId);
    console.log('User preferences:', preferences);
  } catch (error) {
    if (error instanceof ApiError) {
      console.error(`API Error (${error.status}): ${error.message}`);
    } else {
      console.error('Failed to get user preferences:', error);
    }
  }
}

// Update user preferences
async function updateUserPreferences(userId: string) {
  const preferences: UserPreferences = {
    preferred_model: 'anthropic/claude-3-haiku',
    default_tone: 'professional',
    custom_prompts: {
      email: 'Write a professional email about:',
    },
  };

  try {
    const updatedPreferences = await apiService.updateUserPreferences(userId, preferences);
    console.log('Updated preferences:', updatedPreferences);
  } catch (error) {
    if (error instanceof ApiError) {
      console.error(`API Error (${error.status}): ${error.message}`);
    } else {
      console.error('Failed to update user preferences:', error);
    }
  }
}
```

### Error Handling

The library provides a custom `ApiError` class for better error handling:

```typescript
import { ApiService, ApiError } from 'writing-assistant-connector';

const apiService = new ApiService({
  baseUrl: 'http://localhost:8000',
});

async function handleErrors() {
  try {
    const response = await apiService.generateDraft({
      prompt: 'Write something',
    });
    console.log('Success:', response);
  } catch (error) {
    if (error instanceof ApiError) {
      // Handle API-specific errors
      console.error(`API Error (${error.status}): ${error.message}`);

      // You can access the original error if needed
      console.error('Original error:', error.originalError);

      // Handle specific status codes
      if (error.status === 401) {
        console.error('Authentication failed. Please check your API key.');
      } else if (error.status === 429) {
        console.error('Rate limit exceeded. Please try again later.');
      }
    } else {
      // Handle other errors
      console.error('Unexpected error:', error);
    }
  }
}
```

### Request Cancellation

You can cancel ongoing requests using the `cancelRequest` method:

```typescript
import { ApiService } from 'writing-assistant-connector';

const apiService = new ApiService({
  baseUrl: 'http://localhost:8000',
});

// Start a request with a unique ID
const requestId = 'long-running-request';
const draftPromise = apiService.generateDraft({
  prompt: 'Write a very long story...',
  max_length: 10000,
}, requestId);

// Cancel the request if needed (e.g., user clicked cancel button)
setTimeout(() => {
  console.log('Cancelling request...');
  apiService.cancelRequest(requestId);
}, 2000);

try {
  const result = await draftPromise;
  console.log('Result:', result);
} catch (error) {
  if (error.message === 'Request cancelled') {
    console.log('Request was cancelled successfully');
  } else {
    console.error('Error:', error);
  }
}
```

## Data Models

The library provides a rich set of data models and utilities for working with the Writing Assistant API:

### Enums

```typescript
import { LLMModel, TextTone, SummaryFormat, CheckType, IssueSeverity } from 'writing-assistant-connector';

// Available LLM models
console.log(LLMModel.CLAUDE_HAIKU); // 'anthropic/claude-3-haiku'
console.log(LLMModel.GPT_4); // 'openai/gpt-4'

// Text tones for adjustment
console.log(TextTone.PROFESSIONAL); // 'professional'
console.log(TextTone.CASUAL); // 'casual'

// Summary formats
console.log(SummaryFormat.PARAGRAPH); // 'paragraph'
console.log(SummaryFormat.BULLETS); // 'bullets'

// Grammar and style check types
console.log(CheckType.GRAMMAR); // 'grammar'
console.log(CheckType.STYLE); // 'style'

// Issue severity levels
console.log(IssueSeverity.HIGH); // 'high'
console.log(IssueSeverity.MEDIUM); // 'medium'
console.log(IssueSeverity.LOW); // 'low'
```

### Request Factory

The `RequestFactory` class provides methods for creating validated request objects:

```typescript
import { RequestFactory, LLMModel, TextTone, CheckType } from 'writing-assistant-connector';

// Create a draft request
const draftRequest = RequestFactory.createDraftRequest(
  'Write a story about a robot',
  {
    max_length: 500,
    model: LLMModel.CLAUDE_HAIKU,
    temperature: 0.7,
  }
);

// Create a grammar analysis request
const analysisRequest = RequestFactory.createAnalyzeGrammarStyleRequest(
  'Text to analyze',
  {
    checks: [CheckType.GRAMMAR, CheckType.STYLE],
    check_grammar: true,
    check_style: true,
  }
);

// Create a summarize request
const summarizeRequest = RequestFactory.createSummarizeRequest(
  'Text to summarize',
  {
    max_length: 200,
    format: SummaryFormat.BULLETS,
  }
);

// Create a tone adjustment request
const toneRequest = RequestFactory.createAdjustToneRequest(
  'Text to adjust',
  TextTone.PROFESSIONAL,
  {
    preserve_meaning: true,
    strength: 0.8,
  }
);
```

### Response Utilities

The `ResponseUtils` class provides methods for working with API responses:

```typescript
import { ResponseUtils, SummaryFormat, IssueSeverity } from 'writing-assistant-connector';

// Get the most important issues from a grammar analysis
const importantIssues = ResponseUtils.getImportantIssues(analysisResponse, 3);

// Calculate improvement percentage
const percentage = ResponseUtils.calculateImprovementPercentage(analysisResponse);

// Format a summary
const bulletPoints = ResponseUtils.formatSummary(
  'First point. Second point. Third point.',
  SummaryFormat.BULLETS
);
```

## Development

### Setup

```bash
# Clone the repository
git clone <repository-url>

# Install dependencies
npm install

# Build the library
npm run build

# Run tests
npm test
```

### Scripts

- `npm run build` - Build the library
- `npm test` - Run tests
- `npm run lint` - Lint the code
- `npm run format` - Format the code

## License

MIT
