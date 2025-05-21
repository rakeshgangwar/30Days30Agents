import { useState } from 'react';
import aiSuggestionsService from '@/api/aiSuggestionsService';
import { useToast } from '@/components/ui/use-toast';
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
  const { toast } = useToast();
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isGeneratingSuggestions, setIsGeneratingSuggestions] = useState(false);

  // Function to get the maximum character length based on platform
  const getMaxLength = () => {
    if (maxLength) return maxLength;

    if (platform === 'twitter') {
      return 280;
    } else if (platform === 'linkedin') {
      return 3000;
    } else if (platform === 'bluesky') {
      return 300;
    }

    return 1000; // Default
  };

  const handleRequestAiSuggestions = () => {
    setShowSuggestions(true);
  };

  const handleCloseSuggestions = () => {
    setShowSuggestions(false);
  };

  const handleApplySuggestion = async (suggestion: string, feedback?: string) => {
    setIsGeneratingSuggestions(true);

    try {
      // For hashtags, we append them to the content
      if (suggestion.startsWith('#')) {
        onChange(content + ' ' + suggestion);
        return;
      }

      // For other suggestions, we use AI to regenerate the content based on the suggestion
      // Note: We're using the backend API to handle the prompt creation and processing

      // Call the OpenAI API through our content suggestions service
      const response = await aiSuggestionsService.applyContentSuggestion({
        content,
        suggestion,
        persona_id: personaId,
        content_type: contentType,
        platform,
        feedback,
      });

      // Update the content with the AI-generated improved version
      if (response && response.improved_content) {
        console.log('Applying suggestion - Original content:', content);
        console.log('Applying suggestion - Improved content:', response.improved_content);

        // Check if the improved content exceeds the character limit
        const limit = getMaxLength();
        const plainText = response.improved_content.replace(/<[^>]*>/g, '');

        if (limit && plainText.length > limit) {
          console.warn(`Improved content exceeds character limit (${plainText.length}/${limit}). Not applying.`);
          // Show a toast notification to the user
          toast({
            title: "Character limit exceeded",
            description: `The improved content exceeds the limit of ${limit} characters. Try a different suggestion or edit manually.`,
            variant: "destructive"
          });
          console.log(`Character limit exceeded: ${plainText.length}/${limit}`);
        } else {
          // Apply the improved content if it's within limits
          onChange(response.improved_content);
        }
      }
    } catch (error) {
      console.error('Error applying suggestion:', error);
      // If there's an error, just apply the suggestion directly as before
      // This serves as a fallback mechanism
      onChange(suggestion);
    } finally {
      setIsGeneratingSuggestions(false);
    }
  };

  const handleGenerateSuggestions = async (type: string) => {
    setIsGeneratingSuggestions(true);

    try {
      // Call the AI suggestions API
      const response = await aiSuggestionsService.getSuggestions({
        content,
        suggestion_type: type,
        persona_id: personaId,
        content_type: contentType,
        platform
      });

      // Return the suggestions from the API
      return response.suggestions;
    } catch (error) {
      console.error('Error generating suggestions:', error);
      return [];
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
