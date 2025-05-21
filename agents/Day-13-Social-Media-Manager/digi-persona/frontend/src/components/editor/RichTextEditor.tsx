import React, { useEffect, useState } from 'react';
import { useEditor, EditorContent, Editor, BubbleMenu } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import CharacterCount from '@tiptap/extension-character-count';
import Highlight from '@tiptap/extension-highlight';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import { Button } from '@/components/ui/button';
import {
  Bold,
  Italic,
  List,
  ListOrdered,
  Heading1,
  Heading2,
  Quote,
  Link as LinkIcon,
  Image as ImageIcon,
  Hash,
  Sparkles
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface RichTextEditorProps {
  content: string;
  onChange: (content: string) => void;
  placeholder?: string;
  maxLength?: number;
  className?: string;
  contentType?: string;
  platform?: string;
  onRequestAiSuggestions?: () => void;
}

export function RichTextEditor({
  content,
  onChange,
  placeholder = 'Start writing...',
  maxLength,
  className,
  contentType,
  platform,
  onRequestAiSuggestions
}: RichTextEditorProps) {
  const [characterCount, setCharacterCount] = useState(0);

  // Function to calculate character count from HTML content
  const calculateCharacterCount = (htmlContent: string) => {
    // Remove HTML tags and decode HTML entities
    const div = document.createElement('div');
    div.innerHTML = htmlContent;
    const text = div.textContent || div.innerText || '';
    return text.length;
  };

  // Set initial character count
  useEffect(() => {
    setCharacterCount(calculateCharacterCount(content));
  }, []);

  // Set platform-specific character limits
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

  const limit = getMaxLength();

  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder,
      }),
      CharacterCount.configure({
        limit,
      }),
      Highlight,
      Link.configure({
        openOnClick: false,
      }),
      Image,
    ],
    content,
    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      onChange(html);

      // Update character count using our custom function
      // This is more reliable than the built-in character count
      const count = calculateCharacterCount(html);
      setCharacterCount(count);
    },
  });

  // Update content when it changes externally
  useEffect(() => {
    if (editor) {
      // Always update the editor content when the content prop changes
      // This ensures that changes from AI suggestions are always applied
      editor.commands.setContent(content);

      // Update the character count after setting content using our custom function
      const count = calculateCharacterCount(content);
      setCharacterCount(count);
    }
  }, [content, editor]);

  if (!editor) {
    return null;
  }

  const addLink = () => {
    const url = window.prompt('URL');
    if (url) {
      editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run();
    }
  };

  const addImage = () => {
    const url = window.prompt('Image URL');
    if (url) {
      editor.chain().focus().setImage({ src: url }).run();
    }
  };

  const addHashtag = () => {
    editor.chain().focus().insertContent(' #').run();
  };

  return (
    <div className={cn("rich-text-editor border rounded-md", className)}>
      <div className="editor-toolbar flex items-center gap-1 p-2 border-b">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={editor.isActive('bold') ? 'bg-accent' : ''}
          type="button"
        >
          <Bold className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={editor.isActive('italic') ? 'bg-accent' : ''}
          type="button"
        >
          <Italic className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={editor.isActive('heading', { level: 2 }) ? 'bg-accent' : ''}
          type="button"
        >
          <Heading1 className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          className={editor.isActive('heading', { level: 3 }) ? 'bg-accent' : ''}
          type="button"
        >
          <Heading2 className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={editor.isActive('bulletList') ? 'bg-accent' : ''}
          type="button"
        >
          <List className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={editor.isActive('orderedList') ? 'bg-accent' : ''}
          type="button"
        >
          <ListOrdered className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
          className={editor.isActive('blockquote') ? 'bg-accent' : ''}
          type="button"
        >
          <Quote className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={addLink}
          className={editor.isActive('link') ? 'bg-accent' : ''}
          type="button"
        >
          <LinkIcon className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={addImage}
          type="button"
        >
          <ImageIcon className="h-4 w-4" />
        </Button>

        <Button
          variant="ghost"
          size="icon"
          onClick={addHashtag}
          type="button"
        >
          <Hash className="h-4 w-4" />
        </Button>

        {onRequestAiSuggestions && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onRequestAiSuggestions}
            type="button"
            className="ml-auto"
          >
            <Sparkles className="h-4 w-4" />
            <span className="sr-only">AI Suggestions</span>
          </Button>
        )}
      </div>

      <EditorContent editor={editor} className="p-3 min-h-[200px] prose prose-sm max-w-none" />

      <div className="editor-footer flex justify-between items-center p-2 border-t text-xs text-muted-foreground">
        <div>
          {contentType && platform && (
            <span className="mr-2">
              {contentType} • {platform}
            </span>
          )}
        </div>
        <div>
          {characterCount} / {limit} characters
        </div>
      </div>

      {editor && (
        <BubbleMenu editor={editor} tippyOptions={{ duration: 100 }}>
          <div className="flex bg-background border rounded-md shadow-md">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => editor.chain().focus().toggleBold().run()}
              className={editor.isActive('bold') ? 'bg-accent' : ''}
              type="button"
            >
              <Bold className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => editor.chain().focus().toggleItalic().run()}
              className={editor.isActive('italic') ? 'bg-accent' : ''}
              type="button"
            >
              <Italic className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={addLink}
              className={editor.isActive('link') ? 'bg-accent' : ''}
              type="button"
            >
              <LinkIcon className="h-4 w-4" />
            </Button>
          </div>
        </BubbleMenu>
      )}
    </div>
  );
}
