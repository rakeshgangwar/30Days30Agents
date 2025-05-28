import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { uploadDocument, addDocumentUrl, getDocuments } from '../services/api';
import type {Document} from '../types';
import { LuFileText, LuLink, LuFolder, LuImage } from "react-icons/lu";

const Home = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState('');
  const [urlName, setUrlName] = useState('');
  const [urlType, setUrlType] = useState('url'); // Default to regular URL
  const [isLoading, setIsLoading] = useState(false);
  const [useOcr, setUseOcr] = useState(false);
  const [useLlmDescription, setUseLlmDescription] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Error fetching documents:', error);
      toast.error('Error fetching documents');
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleFileUpload = async () => {
    if (!file) {
      toast.warning('Please select a file');
      return;
    }

    setIsLoading(true);
    try {
      const newDoc = await uploadDocument(file);
      setDocuments([...documents, newDoc]);
      setFile(null);
      toast.success('Document uploaded successfully');
      navigate(`/chat/${newDoc.id}`);
    } catch (error) {
      console.error('Error uploading document:', error);
      toast.error('Error uploading document');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUrlSubmit = async () => {
    if (!url) {
      toast.warning('Please enter a URL');
      return;
    }

    if (!urlName) {
      toast.warning('Please enter a name for the URL');
      return;
    }

    // Validate YouTube URL if type is youtube
    if (urlType === 'youtube' && !isValidYoutubeUrl(url)) {
      toast.warning('Please enter a valid YouTube URL');
      return;
    }

    setIsLoading(true);
    try {
      const newDoc = await addDocumentUrl(url, urlName, urlType, useOcr, useLlmDescription);
      setDocuments([...documents, newDoc]);
      setUrl('');
      setUrlName('');
      toast.success(`${urlType === 'youtube' ? 'YouTube video' : urlType === 'audio' ? 'Audio file' : urlType === 'image' ? 'Image' : 'URL'} added successfully`);
      navigate(`/chat/${newDoc.id}`);
    } catch (error) {
      console.error(`Error adding ${urlType}:`, error);
      toast.error(`Error adding ${urlType === 'youtube' ? 'YouTube video' : urlType === 'audio' ? 'audio file' : urlType === 'image' ? 'image' : 'URL'}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to validate YouTube URL
  const isValidYoutubeUrl = (url: string): boolean => {
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    return youtubeRegex.test(url);
  };

  return (
    <div className="max-w-5xl mx-auto px-4">
      <div className="flex flex-col gap-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-2">
            Document Analyser
          </h1>
          <p className="text-lg text-gray-600">
            Upload documents or add URLs for AI-powered analysis
          </p>
        </div>

        <Tabs defaultValue="upload" className="w-full">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <LuFileText className="h-4 w-4" />
              Upload Document
            </TabsTrigger>
            <TabsTrigger value="url" className="flex items-center gap-2">
              <LuLink className="h-4 w-4" />
              Add URL
            </TabsTrigger>
            <TabsTrigger value="youtube" className="flex items-center gap-2">
              <LuLink className="h-4 w-4" />
              YouTube Video
            </TabsTrigger>
            <TabsTrigger value="audio" className="flex items-center gap-2">
              <LuLink className="h-4 w-4" />
              Audio URL
            </TabsTrigger>
            <TabsTrigger value="image" className="flex items-center gap-2">
              <LuImage className="h-4 w-4" />
              Image Analysis
            </TabsTrigger>
            <TabsTrigger value="documents" className="flex items-center gap-2">
              <LuFolder className="h-4 w-4" />
              My Documents
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload">
            <div className="flex flex-col gap-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="file-upload">Upload a document</Label>
                <Input
                  id="file-upload"
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx,.txt,.xlsx,.xls,.pptx,.jpg,.jpeg,.png,.mp3,.wav,.epub,.zip,.csv,.json,.xml"
                  className="p-1"
                />
                <p className="text-sm text-gray-500">
                  Supported formats: PDF, DOC, DOCX, TXT, XLSX, XLS, PPTX, JPG, PNG, MP3, WAV, EPUB, ZIP, CSV, JSON, XML
                </p>
              </div>
              <Button
                onClick={handleFileUpload}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isLoading ? "Uploading..." : "Upload & Analyze"}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="url">
            <div className="flex flex-col gap-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="url-name">Document Name</Label>
                <Input
                  id="url-name"
                  value={urlName}
                  onChange={(e) => setUrlName(e.target.value)}
                  placeholder="Enter a name for this document"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="url-input">URL</Label>
                <Input
                  id="url-input"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/document"
                />
              </div>
              <Button
                onClick={handleUrlSubmit}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isLoading ? "Adding..." : "Add & Analyze"}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="youtube">
            <div className="flex flex-col gap-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="youtube-name">Video Name</Label>
                <Input
                  id="youtube-name"
                  value={urlName}
                  onChange={(e) => setUrlName(e.target.value)}
                  placeholder="Enter a name for this YouTube video"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="youtube-url">YouTube URL</Label>
                <Input
                  id="youtube-url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..."
                />
                <p className="text-sm text-gray-500">
                  Enter a valid YouTube video URL to analyze its transcript
                </p>
              </div>
              <Button
                onClick={() => {
                  setUrlType('youtube');
                  handleUrlSubmit();
                }}
                disabled={isLoading}
                className="bg-red-600 hover:bg-red-700"
              >
                {isLoading ? "Adding..." : "Add YouTube Video & Analyze"}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="audio">
            <div className="flex flex-col gap-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="audio-name">Audio Name</Label>
                <Input
                  id="audio-name"
                  value={urlName}
                  onChange={(e) => setUrlName(e.target.value)}
                  placeholder="Enter a name for this audio file"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="audio-url">Audio URL</Label>
                <Input
                  id="audio-url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/audio.mp3"
                />
                <p className="text-sm text-gray-500">
                  Enter a URL to an audio file (MP3, WAV, etc.) to analyze its content
                </p>
              </div>
              <Button
                onClick={() => {
                  setUrlType('audio');
                  handleUrlSubmit();
                }}
                disabled={isLoading}
                className="bg-purple-600 hover:bg-purple-700"
              >
                {isLoading ? "Adding..." : "Add Audio & Analyze"}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="image">
            <div className="flex flex-col gap-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="image-name">Image Name</Label>
                <Input
                  id="image-name"
                  value={urlName}
                  onChange={(e) => setUrlName(e.target.value)}
                  placeholder="Enter a name for this image"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="image-url">Image URL</Label>
                <Input
                  id="image-url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/image.jpg"
                />
                <p className="text-sm text-gray-500">
                  Enter a URL to an image file (JPG, PNG, etc.) to analyze its content
                </p>
              </div>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="use-ocr"
                    checked={useOcr}
                    onCheckedChange={(checked) => setUseOcr(!!checked)}
                  />
                  <Label htmlFor="use-ocr">Use OCR to extract text from image</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="use-llm-description"
                    checked={useLlmDescription}
                    onCheckedChange={(checked) => setUseLlmDescription(!!checked)}
                  />
                  <Label htmlFor="use-llm-description">Generate image description using AI</Label>
                </div>
              </div>
              <Button
                onClick={() => {
                  setUrlType('image');
                  handleUrlSubmit();
                }}
                disabled={isLoading}
                className="bg-teal-600 hover:bg-teal-700"
              >
                {isLoading ? "Adding..." : "Add Image & Analyze"}
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="documents">
            <div className="mt-4">
              {documents.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {documents.map((doc) => (
                    <Card
                      key={doc.id}
                      className="cursor-pointer hover:shadow-md transition-shadow duration-200"
                      onClick={() => navigate(`/chat/${doc.id}`)}
                    >
                      <CardContent className="p-4">
                        <div className="flex justify-between items-center mb-2">
                          <CardTitle className="text-lg">{doc.name}</CardTitle>
                          <Badge
                            className={`${
                              doc.type === 'file' 
                                ? 'bg-blue-100 text-blue-800' 
                                : doc.type === 'youtube' 
                                  ? 'bg-red-100 text-red-800' 
                                  : doc.type === 'audio' 
                                    ? 'bg-purple-100 text-purple-800' 
                                    : doc.type === 'image' 
                                      ? 'bg-teal-100 text-teal-800' 
                                      : 'bg-green-100 text-green-800'
                            }`}
                          >
                            {doc.type === 'file' 
                              ? 'File' 
                              : doc.type === 'youtube' 
                                ? 'YouTube' 
                                : doc.type === 'audio' 
                                  ? 'Audio' 
                                  : doc.type === 'image' 
                                    ? 'Image' 
                                    : 'URL'}
                          </Badge>
                        </div>
                        <CardDescription>
                          {doc.type === 'file'
                            ? `File: ${doc.name}`
                            : doc.type === 'youtube'
                              ? `YouTube: ${doc.name}`
                              : doc.type === 'audio'
                                ? `Audio: ${doc.name}`
                                : doc.type === 'image'
                                  ? `Image: ${doc.name}`
                                  : `URL: ${doc.url}`}
                        </CardDescription>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-10">
                  <p className="text-lg">No documents yet</p>
                  <p className="text-gray-500">
                    Upload a document or add a URL to get started
                  </p>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Home;
