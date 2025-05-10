import {
  LLMModel,
  TextTone,
  SummaryFormat,
  CheckType,
  IssueSeverity,
  RequestFactory,
  ResponseUtils,
  AnalyzeGrammarStyleResponse,
  TextIssue,
} from '../../src/models/DataModel';

describe('DataModel', () => {
  describe('Enums', () => {
    it('should define LLM models', () => {
      expect(LLMModel.CLAUDE_HAIKU).toBe('anthropic/claude-3-haiku');
      expect(LLMModel.GPT_4).toBe('openai/gpt-4');
    });

    it('should define text tones', () => {
      expect(TextTone.PROFESSIONAL).toBe('professional');
      expect(TextTone.CASUAL).toBe('casual');
    });

    it('should define summary formats', () => {
      expect(SummaryFormat.PARAGRAPH).toBe('paragraph');
      expect(SummaryFormat.BULLETS).toBe('bullets');
    });

    it('should define check types', () => {
      expect(CheckType.GRAMMAR).toBe('grammar');
      expect(CheckType.STYLE).toBe('style');
    });

    it('should define issue severities', () => {
      expect(IssueSeverity.LOW).toBe('low');
      expect(IssueSeverity.MEDIUM).toBe('medium');
      expect(IssueSeverity.HIGH).toBe('high');
    });
  });

  describe('RequestFactory', () => {
    describe('createDraftRequest', () => {
      it('should create a valid draft request', () => {
        const request = RequestFactory.createDraftRequest('Write a story about a robot');
        
        expect(request).toEqual({
          prompt: 'Write a story about a robot',
        });
      });

      it('should include optional parameters', () => {
        const request = RequestFactory.createDraftRequest('Write a story about a robot', {
          context: 'Science fiction setting',
          max_length: 500,
          model: LLMModel.CLAUDE_HAIKU,
          temperature: 0.7,
          user_id: 'user123',
          format: 'markdown',
        });
        
        expect(request).toEqual({
          prompt: 'Write a story about a robot',
          context: 'Science fiction setting',
          max_length: 500,
          model: LLMModel.CLAUDE_HAIKU,
          temperature: 0.7,
          user_id: 'user123',
          format: 'markdown',
        });
      });

      it('should throw an error for empty prompt', () => {
        expect(() => {
          RequestFactory.createDraftRequest('');
        }).toThrow('Prompt is required and cannot be empty');
      });

      it('should throw an error for invalid max_length', () => {
        expect(() => {
          RequestFactory.createDraftRequest('Write a story', { max_length: 0 });
        }).toThrow('max_length must be a positive number');
      });

      it('should throw an error for invalid temperature', () => {
        expect(() => {
          RequestFactory.createDraftRequest('Write a story', { temperature: 1.5 });
        }).toThrow('temperature must be between 0 and 1');
      });
    });

    describe('createAnalyzeGrammarStyleRequest', () => {
      it('should create a valid grammar analysis request', () => {
        const request = RequestFactory.createAnalyzeGrammarStyleRequest('This is a test text.');
        
        expect(request).toEqual({
          text: 'This is a test text.',
        });
      });

      it('should include optional parameters', () => {
        const request = RequestFactory.createAnalyzeGrammarStyleRequest('This is a test text.', {
          checks: [CheckType.GRAMMAR, CheckType.STYLE],
          check_grammar: true,
          check_style: true,
          check_spelling: false,
          language: 'en-US',
          model: LLMModel.GPT_4,
          temperature: 0.3,
          user_id: 'user123',
        });
        
        expect(request).toEqual({
          text: 'This is a test text.',
          checks: [CheckType.GRAMMAR, CheckType.STYLE],
          check_grammar: true,
          check_style: true,
          check_spelling: false,
          language: 'en-US',
          model: LLMModel.GPT_4,
          temperature: 0.3,
          user_id: 'user123',
        });
      });

      it('should throw an error for empty text', () => {
        expect(() => {
          RequestFactory.createAnalyzeGrammarStyleRequest('');
        }).toThrow('Text is required and cannot be empty');
      });
    });

    describe('createSummarizeRequest', () => {
      it('should create a valid summarize request', () => {
        const request = RequestFactory.createSummarizeRequest('This is a long text to summarize.');
        
        expect(request).toEqual({
          text: 'This is a long text to summarize.',
        });
      });

      it('should include optional parameters', () => {
        const request = RequestFactory.createSummarizeRequest('This is a long text to summarize.', {
          max_length: 100,
          format: SummaryFormat.BULLETS,
          focus: 'main points',
          model: LLMModel.CLAUDE_HAIKU,
          temperature: 0.5,
          user_id: 'user123',
        });
        
        expect(request).toEqual({
          text: 'This is a long text to summarize.',
          max_length: 100,
          format: SummaryFormat.BULLETS,
          focus: 'main points',
          model: LLMModel.CLAUDE_HAIKU,
          temperature: 0.5,
          user_id: 'user123',
        });
      });

      it('should throw an error for empty text', () => {
        expect(() => {
          RequestFactory.createSummarizeRequest('');
        }).toThrow('Text is required and cannot be empty');
      });
    });

    describe('createAdjustToneRequest', () => {
      it('should create a valid tone adjustment request', () => {
        const request = RequestFactory.createAdjustToneRequest(
          'This is a casual text.',
          TextTone.PROFESSIONAL
        );
        
        expect(request).toEqual({
          text: 'This is a casual text.',
          target_tone: TextTone.PROFESSIONAL,
        });
      });

      it('should include optional parameters', () => {
        const request = RequestFactory.createAdjustToneRequest(
          'This is a casual text.',
          TextTone.PROFESSIONAL,
          {
            preserve_meaning: true,
            strength: 0.8,
            model: LLMModel.GPT_4,
            temperature: 0.6,
            user_id: 'user123',
          }
        );
        
        expect(request).toEqual({
          text: 'This is a casual text.',
          target_tone: TextTone.PROFESSIONAL,
          preserve_meaning: true,
          strength: 0.8,
          model: LLMModel.GPT_4,
          temperature: 0.6,
          user_id: 'user123',
        });
      });

      it('should throw an error for empty text', () => {
        expect(() => {
          RequestFactory.createAdjustToneRequest('', TextTone.PROFESSIONAL);
        }).toThrow('Text is required and cannot be empty');
      });

      it('should throw an error for empty target tone', () => {
        expect(() => {
          RequestFactory.createAdjustToneRequest('This is a text.', '');
        }).toThrow('Target tone is required and cannot be empty');
      });
    });
  });

  describe('ResponseUtils', () => {
    describe('getImportantIssues', () => {
      it('should return the most important issues sorted by severity', () => {
        const response: AnalyzeGrammarStyleResponse = {
          issues: [
            { type: 'grammar', description: 'Minor issue', suggestion: 'Fix it', severity: IssueSeverity.LOW },
            { type: 'style', description: 'Major issue', suggestion: 'Fix it', severity: IssueSeverity.HIGH },
            { type: 'spelling', description: 'Medium issue', suggestion: 'Fix it', severity: IssueSeverity.MEDIUM },
            { type: 'grammar', description: 'Another major issue', suggestion: 'Fix it', severity: IssueSeverity.HIGH },
            { type: 'clarity', description: 'Another medium issue', suggestion: 'Fix it', severity: IssueSeverity.MEDIUM },
            { type: 'style', description: 'Another minor issue', suggestion: 'Fix it', severity: IssueSeverity.LOW },
          ],
          improved_text: 'Improved text',
          model_used: 'test-model',
        };

        const importantIssues = ResponseUtils.getImportantIssues(response, 3);
        
        expect(importantIssues).toHaveLength(3);
        expect(importantIssues[0].severity).toBe(IssueSeverity.HIGH);
        expect(importantIssues[1].severity).toBe(IssueSeverity.HIGH);
        expect(importantIssues[2].severity).toBe(IssueSeverity.MEDIUM);
      });

      it('should return all issues if maxIssues is greater than issues length', () => {
        const response: AnalyzeGrammarStyleResponse = {
          issues: [
            { type: 'grammar', description: 'Issue 1', suggestion: 'Fix it', severity: IssueSeverity.LOW },
            { type: 'style', description: 'Issue 2', suggestion: 'Fix it', severity: IssueSeverity.MEDIUM },
          ],
          improved_text: 'Improved text',
          model_used: 'test-model',
        };

        const importantIssues = ResponseUtils.getImportantIssues(response, 5);
        
        expect(importantIssues).toHaveLength(2);
      });
    });

    describe('calculateImprovementPercentage', () => {
      it('should calculate improvement percentage based on issues', () => {
        const response: AnalyzeGrammarStyleResponse = {
          issues: [
            { type: 'grammar', description: 'Issue 1', suggestion: 'Fix it', severity: IssueSeverity.LOW },
            { type: 'style', description: 'Issue 2', suggestion: 'Fix it', severity: IssueSeverity.MEDIUM },
          ],
          improved_text: 'This is a long improved text with many characters to test the ratio calculation.',
          model_used: 'test-model',
        };

        const percentage = ResponseUtils.calculateImprovementPercentage(response);
        
        expect(percentage).toBeGreaterThan(0);
        expect(percentage).toBeLessThanOrEqual(100);
      });

      it('should return 0 if there are no issues', () => {
        const response: AnalyzeGrammarStyleResponse = {
          issues: [],
          improved_text: 'Improved text',
          model_used: 'test-model',
        };

        const percentage = ResponseUtils.calculateImprovementPercentage(response);
        
        expect(percentage).toBe(0);
      });
    });

    describe('formatSummary', () => {
      it('should convert paragraph to bullet points', () => {
        const summary = 'First point. Second point. Third point.';
        const formatted = ResponseUtils.formatSummary(summary, SummaryFormat.BULLETS);
        
        expect(formatted).toContain('• First point');
        expect(formatted).toContain('• Second point');
        expect(formatted).toContain('• Third point');
        expect(formatted.split('\n')).toHaveLength(3);
      });

      it('should convert bullet points to paragraph', () => {
        const summary = '• First point\n• Second point\n• Third point';
        const formatted = ResponseUtils.formatSummary(summary, SummaryFormat.PARAGRAPH);
        
        expect(formatted).toBe('First point Second point Third point');
      });

      it('should return the original summary if already in the requested format', () => {
        const bulletSummary = '• First point\n• Second point';
        const paragraphSummary = 'First point. Second point.';
        
        expect(ResponseUtils.formatSummary(bulletSummary, SummaryFormat.BULLETS)).toBe(bulletSummary);
        expect(ResponseUtils.formatSummary(paragraphSummary, SummaryFormat.PARAGRAPH)).toBe(paragraphSummary);
      });
    });
  });
});
