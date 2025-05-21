import { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Sparkles, Check, X, RefreshCw, ThumbsUp, ThumbsDown, Zap, Lightbulb, Megaphone, Hash } from 'lucide-react';
import { Textarea } from '@/components/ui/textarea';

interface AiSuggestionsProps {
  content: string; // Needed for API calls even if not directly used in component
  onApplySuggestion: (suggestion: string, feedback?: string) => void;
  onClose: () => void;
  contentType?: string;
  platform?: string;
  persona?: {
    id: number;
    name: string;
  };
  isGenerating?: boolean;
  onGenerateSuggestions: (type: string) => Promise<any>; // Changed return type to any
}

// Define the Suggestion type
interface Suggestion {
  id: string;
  text: string;
  type: string;
  description?: string;
}

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
  // State to track global feedback for all suggestions
  const [feedback, setFeedback] = useState('');

  // Default tab categories
  const tabCategories = ['improve', 'tone', 'hashtags', 'engagement'];

  // Function to handle generating suggestions
  const handleGenerateSuggestions = async () => {
    try {
      // Call the onGenerateSuggestions function which will make the API request
      const result = await onGenerateSuggestions(activeTab);

      // If we received suggestions from the API, update the state
      if (result) {
        setSuggestions(prevSuggestions => ({
          ...prevSuggestions,
          [activeTab]: result
        }));
      }
    } catch (error) {
      console.error('Error generating suggestions:', error);
    }
  };

  // Function to apply a suggestion with global feedback
  const applySuggestion = (suggestion: Suggestion) => {
    onApplySuggestion(suggestion.text, feedback);
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
          <TabsList className="w-full grid grid-cols-4 h-auto">
            <TabsTrigger value="improve" className="flex flex-col h-auto py-2 px-1">
              <Zap className="h-4 w-4 mb-1" />
              <span className="text-xs">Improve</span>
            </TabsTrigger>
            <TabsTrigger value="tone" className="flex flex-col h-auto py-2 px-1">
              <Megaphone className="h-4 w-4 mb-1" />
              <span className="text-xs">Tone</span>
            </TabsTrigger>
            <TabsTrigger value="hashtags" className="flex flex-col h-auto py-2 px-1">
              <Hash className="h-4 w-4 mb-1" />
              <span className="text-xs">Tags</span>
            </TabsTrigger>
            <TabsTrigger value="engagement" className="flex flex-col h-auto py-2 px-1">
              <Lightbulb className="h-4 w-4 mb-1" />
              <span className="text-xs">Engage</span>
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
                            disabled={isGenerating}
                          >
                            {isGenerating ? (
                              <RefreshCw className="h-4 w-4 animate-spin" />
                            ) : (
                              <Check className="h-4 w-4" />
                            )}
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
              {/* Global Feedback Textarea */}
              <div className="px-4 pb-2">
                <Textarea
                  placeholder="Optional: Add feedback to guide the AI for any suggestion..."
                  value={feedback}
                  onChange={e => setFeedback(e.target.value)}
                  className="min-h-[48px] text-xs mt-2"
                  disabled={isGenerating}
                />
                <Button
                  className="mt-2 w-full font-semibold shadow-md"
                  variant="default"
                  size="lg"
                  onClick={() => onApplySuggestion('', feedback)}
                  disabled={!feedback.trim() || isGenerating}
                >
                  {isGenerating ? (
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Sparkles className="h-4 w-4 mr-2 text-primary" />
                  )}
                  Apply Feedback
                </Button>
              </div>
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
