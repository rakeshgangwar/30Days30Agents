/**
 * Tests for the main index.ts exports
 */

import * as WritingAssistant from '../src';

describe('Index Exports', () => {
  it('should export ApiService', () => {
    expect(WritingAssistant.ApiService).toBeDefined();
    expect(typeof WritingAssistant.ApiService).toBe('function');
  });

  it('should export ApiError', () => {
    expect(WritingAssistant.ApiError).toBeDefined();
    expect(typeof WritingAssistant.ApiError).toBe('function');
  });

  it('should export RequestFactory', () => {
    expect(WritingAssistant.RequestFactory).toBeDefined();
    expect(typeof WritingAssistant.RequestFactory).toBe('function');
  });

  it('should export ResponseUtils', () => {
    expect(WritingAssistant.ResponseUtils).toBeDefined();
    expect(typeof WritingAssistant.ResponseUtils).toBe('function');
  });

  it('should export enums', () => {
    expect(WritingAssistant.LLMModel).toBeDefined();
    expect(WritingAssistant.TextTone).toBeDefined();
    expect(WritingAssistant.SummaryFormat).toBeDefined();
    expect(WritingAssistant.CheckType).toBeDefined();
    expect(WritingAssistant.IssueSeverity).toBeDefined();
  });

  it('should export request interfaces', () => {
    // We can't directly test interfaces, but we can check if they're used in the factory methods
    const draftRequest = WritingAssistant.RequestFactory.createDraftRequest('test');
    expect(draftRequest).toHaveProperty('prompt');

    const analyzeRequest = WritingAssistant.RequestFactory.createAnalyzeGrammarStyleRequest('test');
    expect(analyzeRequest).toHaveProperty('text');

    const summarizeRequest = WritingAssistant.RequestFactory.createSummarizeRequest('test');
    expect(summarizeRequest).toHaveProperty('text');

    const toneRequest = WritingAssistant.RequestFactory.createAdjustToneRequest('test', 'professional');
    expect(toneRequest).toHaveProperty('text');
    expect(toneRequest).toHaveProperty('target_tone');
  });
});
