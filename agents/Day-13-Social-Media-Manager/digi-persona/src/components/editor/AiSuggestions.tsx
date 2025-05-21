import React, { useState } from 'react';
import aiSuggestionsService, { Suggestion as SuggestionType } from '@/api/aiSuggestionsService';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Sparkles, Check, X, RefreshCw, ThumbsUp, ThumbsDown, Zap, Lightbulb, Megaphone, Hash } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AiSuggestionsProps {
  content: string;
  onApplySuggestion: (suggestion: string) => void;
  onClose: () => void;
  contentType?: string;
  platform?: string;
  persona?: {
    id: number;
    name: string;
  };
  isGenerating?: boolean;
  onGenerateSuggestions: (type: string) => Promise<void>;
}

// Using the type from our API service
type Suggestion = SuggestionType;

export function AiSuggestions({
  content,
  onApplySuggestion,
  onClose,
  contentType,
  platform,
  persona,
  isGenerating = false,
  onGenerateSuggestions
}: AiSuggestionsProps) {
  const [activeTab, setActiveTab] = useState('improve');
  const [suggestions, setSuggestions] = useState<Record<string, Suggestion[]>>({
    improve: [],
    tone: [],
    hashtags: [],
    engagement: []
  });

  // Default tab categories
  const tabCategories = ['improve', 'tone', 'hashtags', 'engagement'];

  // Function to handle generating suggestions
  const handleGenerateSuggestions = async () => {
    try {
      await onGenerateSuggestions(activeTab);

      // Call the API to get suggestions
      const response = await aiSuggestionsService.getSuggestions({
        content,
        suggestion_type: activeTab,
        persona_id: persona?.id,
        content_type: contentType,
        platform: platform
      });

      // Update the suggestions state with the API response
      setSuggestions(prevSuggestions => ({
        ...prevSuggestions,
        [activeTab]: response.suggestions
      }));
    } catch (error) {
      console.error('Error generating suggestions:', error);
    }
  };

  // Function to apply a suggestion
  const applySuggestion = (suggestion: Suggestion) => {
    onApplySuggestion(suggestion.text);
  };

  const getTabIcon = (tab: string) => {
    switch (tab) {
      case 'improve':
        return <Zap className="h-4 w-4" />;
      case 'tone':
        return <Megaphone className="h-4 w-4" />;
      case 'hashtags':
        return <Hash className="h-4 w-4" />;
      case 'engagement':
        return <Lightbulb className="h-4 w-4" />;
      default:
        return <Sparkles className="h-4 w-4" />;
    }
  };

  return (
    <Card className="w-full max-w-md">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            AI Suggestions
          </CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        <CardDescription>
          Get AI-powered suggestions to improve your content
          {persona && ` as ${persona.name}`}
        </CardDescription>
      </CardHeader>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="px-4">
          <TabsList className="w-full">
            <TabsTrigger value="improve" className="flex-1">
              <Zap className="h-4 w-4 mr-2" />
              Improve
            </TabsTrigger>
            <TabsTrigger value="tone" className="flex-1">
              <Megaphone className="h-4 w-4 mr-2" />
              Tone
            </TabsTrigger>
            <TabsTrigger value="hashtags" className="flex-1">
              <Hash className="h-4 w-4 mr-2" />
              Hashtags
            </TabsTrigger>
            <TabsTrigger value="engagement" className="flex-1">
              <Lightbulb className="h-4 w-4 mr-2" />
              Engagement
            </TabsTrigger>
          </TabsList>
        </div>

        {tabCategories.map((tab) => (
          <TabsContent key={tab} value={tab} className="mt-0">
            <CardContent className="pt-4">
              {suggestions[tab]?.length > 0 ? (
                <div className="space-y-3">
                  {suggestions[tab].map((suggestion) => (
                    <div key={suggestion.id} className="p-3 border rounded-md">
                      <div className="flex justify-between items-start gap-2">
                        <div>
                          <p className="text-sm">{suggestion.text}</p>
                          {suggestion.description && (
                            <p className="text-xs text-muted-foreground mt-1">{suggestion.description}</p>
                          )}
                        </div>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => applySuggestion(suggestion)}
                            className="h-7 w-7"
                          >
                            <Check className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="flex gap-1 mt-2">
                        <Button variant="ghost" size="sm" className="h-6 text-xs">
                          <ThumbsUp className="h-3 w-3 mr-1" />
                          Helpful
                        </Button>
                        <Button variant="ghost" size="sm" className="h-6 text-xs">
                          <ThumbsDown className="h-3 w-3 mr-1" />
                          Not helpful
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-6">
                  <div className="text-center">
                    <div className="flex justify-center mb-3">
                      {getTabIcon(tab)}
                    </div>
                    <p className="text-sm text-muted-foreground mb-4">
                      {tab === 'improve' && 'Get suggestions to improve your content structure and clarity.'}
                      {tab === 'tone' && 'Adjust your tone to better match your persona and audience.'}
                      {tab === 'hashtags' && 'Get relevant hashtag suggestions for your content.'}
                      {tab === 'engagement' && 'Increase engagement with better calls-to-action.'}
                    </p>
                    <Button
                      onClick={handleGenerateSuggestions}
                      disabled={isGenerating}
                      className="w-full"
                    >
                      {isGenerating ? (
                        <>
                          <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <Sparkles className="h-4 w-4 mr-2" />
                          Generate Suggestions
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </TabsContent>
        ))}
      </Tabs>

      <CardFooter className="flex justify-between border-t pt-3">
        <div className="text-xs text-muted-foreground">
          {contentType && platform && (
            <span>
              {contentType} • {platform}
            </span>
          )}
        </div>
        {suggestions[activeTab]?.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleGenerateSuggestions}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            Refresh
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
