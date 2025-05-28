import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toaster } from './ui/toaster.tsx';
import { addDocumentUrl } from '../services/api';
import type {Document} from '../types';

interface UrlInputProps {
  onUrlSuccess?: (document: Document) => void;
}

const UrlInput = ({ onUrlSuccess }: UrlInputProps) => {
  const [url, setUrl] = useState('');
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!url) {
      toaster.create({
        title: 'Warning',
        description: 'Please enter a URL',
        type: 'warning',
      });
      return;
    }

    if (!name) {
      toaster.create({
        title: 'Warning',
        description: 'Please enter a name for the URL',
        type: 'warning',
      });
      return;
    }

    setIsLoading(true);
    try {
      const newDoc = await addDocumentUrl(url, name);
      setUrl('');
      setName('');
      toaster.create({
        title: 'Success',
        description: 'URL added successfully',
        type: 'success',
      });
      
      if (onUrlSuccess) {
        onUrlSuccess(newDoc);
      }
    } catch (error) {
      console.error('Error adding URL:', error);
      toaster.create({
        title: 'Error',
        description: 'Error adding URL',
        type: 'error',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="space-y-2">
        <Label htmlFor="document-name">Document Name</Label>
        <Input
          id="document-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter a name for this document"
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="document-url">URL</Label>
        <Input
          id="document-url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/document"
        />
      </div>
      
      <Button
        onClick={handleSubmit}
        disabled={isLoading}
        className="bg-blue-600 hover:bg-blue-700"
      >
        {isLoading ? "Adding..." : "Add & Analyze"}
      </Button>
    </div>
  );
};

export default UrlInput;
