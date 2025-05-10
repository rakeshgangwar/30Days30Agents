/**
 * Data models for the Writing Assistant API
 *
 * These classes and interfaces define the structure of the request and response objects
 * for the Writing Assistant API endpoints, along with validation and utility methods.
 */

/**
 * Model information from OpenRouter
 */
export interface ModelInfo {
  /** Model identifier (e.g., 'anthropic/claude-3-haiku') */
  id: string;
  /** Display name of the model */
  name: string;
  /** Optional description of the model */
  description?: string;
  /** Maximum context length in tokens */
  context_length?: number;
  /** Pricing information */
  pricing?: Record<string, any>;
  /** Provider of the model (e.g., 'anthropic', 'openai') */
  provider?: string;
}

/**
 * Available LLM models that can be used with the Writing Assistant
 *
 * Note: This enum is provided for backward compatibility.
 * New code should use the dynamic model list from the API.
 */
export enum LLMModel {
  CLAUDE_HAIKU = 'anthropic/claude-3-haiku',
  CLAUDE_SONNET = 'anthropic/claude-3-sonnet',
  CLAUDE_OPUS = 'anthropic/claude-3-opus',
  GPT_4 = 'openai/gpt-4',
  GPT_4_TURBO = 'openai/gpt-4-turbo',
  GPT_3_5_TURBO = 'openai/gpt-3.5-turbo',
}

/**
 * Tone options for text adjustment
 */
export enum TextTone {
  PROFESSIONAL = 'professional',
  CASUAL = 'casual',
  FRIENDLY = 'friendly',
  FORMAL = 'formal',
  ACADEMIC = 'academic',
  TECHNICAL = 'technical',
  PERSUASIVE = 'persuasive',
  ENTHUSIASTIC = 'enthusiastic',
  CONFIDENT = 'confident',
  EMPATHETIC = 'empathetic',
}

/**
 * Format options for summarization
 */
export enum SummaryFormat {
  PARAGRAPH = 'paragraph',
  BULLETS = 'bullets',
}

/**
 * Grammar and style check types
 */
export enum CheckType {
  GRAMMAR = 'grammar',
  STYLE = 'style',
  SPELLING = 'spelling',
  CLARITY = 'clarity',
  CONCISENESS = 'conciseness',
  TONE = 'tone',
}

/**
 * Severity levels for text issues
 */
export enum IssueSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
}

/**
 * Base request interface with common properties
 */
export interface BaseRequest {
  /** Optional user ID for personalized results */
  user_id?: string;
  /** LLM model to use for the request */
  model?: string;
  /** Temperature setting for the LLM (0.0-1.0) */
  temperature?: number;
}

/**
 * Request for the /draft endpoint
 */
export interface DraftRequest extends BaseRequest {
  /** The prompt to generate text from */
  prompt: string;
  /** Optional context to provide additional information for the generation */
  context?: string;
  /** Optional maximum length of the generated text in characters (no limit if not specified) */
  max_length?: number;
  /** Optional format for the output */
  format?: string;
}

/**
 * Response from the /draft endpoint
 */
export interface DraftResponse {
  /** The generated text */
  text: string;
  /** The model used to generate the text */
  model_used: string;
}

/**
 * Request for the /analyze_grammar_style endpoint
 */
export interface AnalyzeGrammarStyleRequest extends BaseRequest {
  /** The text to analyze */
  text: string;
  /** Types of checks to perform */
  checks?: string[];
  /** Whether to check grammar */
  check_grammar?: boolean;
  /** Whether to check style */
  check_style?: boolean;
  /** Whether to check spelling */
  check_spelling?: boolean;
  /** Language code for the text */
  language?: string;
}

/**
 * Issue found during grammar/style analysis
 */
export interface TextIssue {
  /** Type of issue (grammar, style, spelling, etc.) */
  type: string;
  /** Description of the issue */
  description: string;
  /** Suggested correction */
  suggestion: string;
  /** Severity of the issue */
  severity: IssueSeverity;
  /** Optional position of the issue in the text [start, end] */
  position?: [number, number];
}

/**
 * Response from the /analyze_grammar_style endpoint
 */
export interface AnalyzeGrammarStyleResponse {
  /** List of issues found in the text */
  issues: TextIssue[];
  /** Improved version of the text with corrections */
  improved_text: string;
  /** The model used for analysis */
  model_used: string;
  /** Optional raw analysis data */
  raw_analysis?: string;
}

/**
 * Request for the /summarize endpoint
 */
export interface SummarizeRequest extends BaseRequest {
  /** The text to summarize */
  text: string;
  /** Maximum length of the summary in characters */
  max_length?: number;
  /** Format of the summary */
  format?: SummaryFormat | string;
  /** Optional focus area for the summary */
  focus?: string;
}

/**
 * Response from the /summarize endpoint
 */
export interface SummarizeResponse {
  /** The generated summary */
  summary: string;
  /** The model used for summarization */
  model_used: string;
  /** Length of the original text in characters */
  original_length?: number;
  /** Length of the summary in characters */
  summary_length?: number;
}

/**
 * Request for the /adjust_tone endpoint
 */
export interface AdjustToneRequest extends BaseRequest {
  /** The text to adjust */
  text: string;
  /** Target tone for the adjustment */
  target_tone: TextTone | string;
  /** Whether to preserve the original meaning */
  preserve_meaning?: boolean;
  /** Strength of the tone adjustment (0.0-1.0) */
  strength?: number;
}

/**
 * Response from the /adjust_tone endpoint
 */
export interface AdjustToneResponse {
  /** The original text */
  original_text: string;
  /** The adjusted text */
  adjusted_text: string;
  /** The target tone used for adjustment */
  target_tone: string;
  /** The model used for tone adjustment */
  model_used: string;
}

/**
 * User preferences
 */
export interface UserPreferences {
  /** Preferred LLM model */
  preferred_model?: string;
  /** Default tone for text adjustments */
  default_tone?: string;
  /** Custom prompts for different tasks */
  custom_prompts?: Record<string, string>;
}

/**
 * Utility class for creating and validating requests
 */
export class RequestFactory {
  /**
   * Create a draft request with validation
   * @param prompt The prompt to generate text from
   * @param options Additional options
   * @returns A validated DraftRequest
   * @throws Error if validation fails
   */
  static createDraftRequest(
    prompt: string,
    options?: {
      context?: string;
      max_length?: number;
      model?: string;
      temperature?: number;
      user_id?: string;
      format?: string;
    }
  ): DraftRequest {
    if (!prompt || prompt.trim().length === 0) {
      throw new Error('Prompt is required and cannot be empty');
    }

    const request: DraftRequest = {
      prompt,
    };

    if (options) {
      if (options.context) request.context = options.context;
      if (options.max_length !== undefined) {
        if (options.max_length < 1) {
          throw new Error('max_length must be a positive number');
        }
        request.max_length = options.max_length;
      }
      if (options.model) request.model = options.model;
      if (options.temperature !== undefined) {
        if (options.temperature < 0 || options.temperature > 1) {
          throw new Error('temperature must be between 0 and 1');
        }
        request.temperature = options.temperature;
      }
      if (options.user_id) request.user_id = options.user_id;
      if (options.format) request.format = options.format;
    }

    return request;
  }

  /**
   * Create a grammar analysis request with validation
   * @param text The text to analyze
   * @param options Additional options
   * @returns A validated AnalyzeGrammarStyleRequest
   * @throws Error if validation fails
   */
  static createAnalyzeGrammarStyleRequest(
    text: string,
    options?: {
      checks?: string[];
      check_grammar?: boolean;
      check_style?: boolean;
      check_spelling?: boolean;
      language?: string;
      model?: string;
      temperature?: number;
      user_id?: string;
    }
  ): AnalyzeGrammarStyleRequest {
    if (!text || text.trim().length === 0) {
      throw new Error('Text is required and cannot be empty');
    }

    const request: AnalyzeGrammarStyleRequest = {
      text,
    };

    if (options) {
      if (options.checks) request.checks = options.checks;
      if (options.check_grammar !== undefined) request.check_grammar = options.check_grammar;
      if (options.check_style !== undefined) request.check_style = options.check_style;
      if (options.check_spelling !== undefined) request.check_spelling = options.check_spelling;
      if (options.language) request.language = options.language;
      if (options.model) request.model = options.model;
      if (options.temperature !== undefined) {
        if (options.temperature < 0 || options.temperature > 1) {
          throw new Error('temperature must be between 0 and 1');
        }
        request.temperature = options.temperature;
      }
      if (options.user_id) request.user_id = options.user_id;
    }

    return request;
  }

  /**
   * Create a summarize request with validation
   * @param text The text to summarize
   * @param options Additional options
   * @returns A validated SummarizeRequest
   * @throws Error if validation fails
   */
  static createSummarizeRequest(
    text: string,
    options?: {
      max_length?: number;
      format?: SummaryFormat | string;
      focus?: string;
      model?: string;
      temperature?: number;
      user_id?: string;
    }
  ): SummarizeRequest {
    if (!text || text.trim().length === 0) {
      throw new Error('Text is required and cannot be empty');
    }

    const request: SummarizeRequest = {
      text,
    };

    if (options) {
      if (options.max_length !== undefined) {
        if (options.max_length < 1) {
          throw new Error('max_length must be a positive number');
        }
        request.max_length = options.max_length;
      }
      if (options.format) request.format = options.format;
      if (options.focus) request.focus = options.focus;
      if (options.model) request.model = options.model;
      if (options.temperature !== undefined) {
        if (options.temperature < 0 || options.temperature > 1) {
          throw new Error('temperature must be between 0 and 1');
        }
        request.temperature = options.temperature;
      }
      if (options.user_id) request.user_id = options.user_id;
    }

    return request;
  }

  /**
   * Create a tone adjustment request with validation
   * @param text The text to adjust
   * @param target_tone The target tone
   * @param options Additional options
   * @returns A validated AdjustToneRequest
   * @throws Error if validation fails
   */
  static createAdjustToneRequest(
    text: string,
    target_tone: TextTone | string,
    options?: {
      preserve_meaning?: boolean;
      strength?: number;
      model?: string;
      temperature?: number;
      user_id?: string;
    }
  ): AdjustToneRequest {
    if (!text || text.trim().length === 0) {
      throw new Error('Text is required and cannot be empty');
    }

    if (!target_tone || target_tone.trim().length === 0) {
      throw new Error('Target tone is required and cannot be empty');
    }

    const request: AdjustToneRequest = {
      text,
      target_tone,
    };

    if (options) {
      if (options.preserve_meaning !== undefined) request.preserve_meaning = options.preserve_meaning;
      if (options.strength !== undefined) {
        if (options.strength < 0 || options.strength > 1) {
          throw new Error('strength must be between 0 and 1');
        }
        request.strength = options.strength;
      }
      if (options.model) request.model = options.model;
      if (options.temperature !== undefined) {
        if (options.temperature < 0 || options.temperature > 1) {
          throw new Error('temperature must be between 0 and 1');
        }
        request.temperature = options.temperature;
      }
      if (options.user_id) request.user_id = options.user_id;
    }

    return request;
  }
}

/**
 * Utility functions for working with responses
 */
export class ResponseUtils {
  /**
   * Extract the most important issues from a grammar analysis response
   * @param response The analysis response
   * @param maxIssues Maximum number of issues to return
   * @returns The most important issues
   */
  static getImportantIssues(response: AnalyzeGrammarStyleResponse, maxIssues: number = 5): TextIssue[] {
    // Sort issues by severity (high to low)
    const sortedIssues = [...response.issues].sort((a, b) => {
      const severityOrder = { high: 3, medium: 2, low: 1 };
      return severityOrder[b.severity] - severityOrder[a.severity];
    });

    // Return the top N issues
    return sortedIssues.slice(0, maxIssues);
  }

  /**
   * Calculate the improvement percentage between original and improved text
   * @param response The analysis response
   * @returns Percentage of improvement
   */
  static calculateImprovementPercentage(response: AnalyzeGrammarStyleResponse): number {
    if (!response.issues.length) return 0;

    // A simple heuristic: 100% - (issues.length / original text length * 100)
    // This gives a rough estimate of how "clean" the text is
    const issueRatio = response.issues.length / response.improved_text.length;
    const improvementPercentage = Math.max(0, Math.min(100, 100 - (issueRatio * 1000)));

    return Math.round(improvementPercentage);
  }

  /**
   * Format a summary based on the requested format
   * @param summary The summary text
   * @param format The desired format
   * @returns Formatted summary
   */
  static formatSummary(summary: string, format: SummaryFormat | string): string {
    if (format === SummaryFormat.BULLETS) {
      // Convert paragraph to bullet points if it's not already
      if (!summary.includes('• ')) {
        const sentences = summary
          .split(/[.!?]/)
          .map(s => s.trim())
          .filter(s => s.length > 0);

        return sentences.map(s => `• ${s}`).join('\n');
      }
    } else if (format === SummaryFormat.PARAGRAPH) {
      // Convert bullet points to paragraph if needed
      if (summary.includes('• ')) {
        return summary
          .split('\n')
          .map(line => line.replace(/^•\s*/, ''))
          .join(' ');
      }
    }

    return summary;
  }
}
