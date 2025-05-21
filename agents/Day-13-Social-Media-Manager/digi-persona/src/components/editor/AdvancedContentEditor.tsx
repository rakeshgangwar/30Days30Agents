import React, { useState } from 'react';
import aiSuggestionsService from '@/api/aiSuggestionsService';
import { RichTextEditor } from './RichTextEditor';
import { AiSuggestions } from './AiSuggestions';
import { Button } from '@/components/ui/button';
import { Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AdvancedContentEditorProps {
  content: string;
  onChange: (content: string) => void;
  placeholder?: string;
  maxLength?: number;
  className?: string;
  contentType?: string;
  platform?: string;
  personaId?: number;
  personaName?: string;
}

export function AdvancedContentEditor({
  content,
  onChange,
  placeholder,
  maxLength,
  className,
  contentType,
  platform,
  personaId,
  personaName
}: AdvancedContentEditorProps) {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isGeneratingSuggestions, setIsGeneratingSuggestions] = useState(false);

  const handleRequestAiSuggestions = () => {
    setShowSuggestions(true);
  };

  const handleCloseSuggestions = () => {
    setShowSuggestions(false);
  };

  const handleApplySuggestion = (suggestion: string) => {
    // For hashtags, we append them to the content
    if (suggestion.startsWith('#')) {
      onChange(content + ' ' + suggestion);
    } else {
      // For other suggestions, we replace the content
      onChange(suggestion);
    }
  };

  const handleGenerateSuggestions = async (type: string) => {
    setIsGeneratingSuggestions(true);

    try {
      // Call the suggestions API
      await aiSuggestionsService.getSuggestions({
        content,
        suggestion_type: type,
        persona_id: personaId,
        content_type: contentType,
        platform
      });
    } catch (error) {
      console.error('Error generating suggestions:', error);
    } finally {
      setIsGeneratingSuggestions(false);
    }
  };

  return (
    <div className={cn("advanced-content-editor", className)}>
      <div className="flex gap-4">
        <div className="flex-1">
          <RichTextEditor
            content={content}
            onChange={onChange}
            placeholder={placeholder}
            maxLength={maxLength}
            contentType={contentType}
            platform={platform}
            onRequestAiSuggestions={handleRequestAiSuggestions}
          />
        </div>

        {showSuggestions && (
          <div className="w-80">
            <AiSuggestions
              content={content}
              onApplySuggestion={handleApplySuggestion}
              onClose={handleCloseSuggestions}
              contentType={contentType}
              platform={platform}
              persona={personaId && personaName ? { id: personaId, name: personaName } : undefined}
              isGenerating={isGeneratingSuggestions}
              onGenerateSuggestions={handleGenerateSuggestions}
            />
          </div>
        )}
      </div>

      {!showSuggestions && (
        <div className="mt-2 flex justify-end">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRequestAiSuggestions}
            className="gap-1"
          >
            <Sparkles className="h-4 w-4" />
            AI Suggestions
          </Button>
        </div>
      )}
    </div>
  );
}
