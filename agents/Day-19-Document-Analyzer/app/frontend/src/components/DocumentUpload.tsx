import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toaster } from './ui/toaster';
import { uploadDocument } from '../services/api';
import type {Document} from '../types';

interface DocumentUploadProps {
  onUploadSuccess?: (document: Document) => void;
}

const DocumentUpload = ({ onUploadSuccess }: DocumentUploadProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toaster.create({
        title: 'Warning',
        description: 'Please select a file',
        type: 'warning',
      });
      return;
    }

    setIsLoading(true);
    try {
      const newDoc = await uploadDocument(file);
      setFile(null);
      toaster.create({
        title: 'Success',
        description: 'Document uploaded successfully',
        type: 'success',
      });
      
      if (onUploadSuccess) {
        onUploadSuccess(newDoc);
      }
    } catch (error) {
      console.error('Error uploading document:', error);
      toaster.create({
        title: 'Error',
        description: 'Error uploading document',
        type: 'error',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="space-y-2">
        <Label htmlFor="file-upload">Upload a document</Label>
        <Input
          id="file-upload"
          type="file"
          onChange={handleFileChange}
          accept=".pdf,.doc,.docx,.txt"
          className="p-1"
        />
        <p className="text-sm text-gray-500">
          Supported formats: PDF, DOC, DOCX, TXT
        </p>
      </div>
      <Button
        onClick={handleUpload}
        disabled={isLoading}
        className="bg-blue-600 hover:bg-blue-700"
      >
        {isLoading ? "Uploading..." : "Upload & Analyze"}
      </Button>
    </div>
  );
};

export default DocumentUpload;
