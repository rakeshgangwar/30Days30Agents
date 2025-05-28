import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type {Document} from '../types';

interface DocumentListProps {
  documents: Document[];
}

const DocumentList = ({ documents }: DocumentListProps) => {
  const navigate = useNavigate();

  const openDocument = (id: string) => {
    navigate(`/chat/${id}`);
  };

  if (documents.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-lg text-gray-500">
          No documents yet. Upload a document or add a URL to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {documents.map((doc) => (
        <Card
          key={doc.id}
          className="cursor-pointer hover:shadow-md hover:-translate-y-0.5 transition-all duration-200"
          onClick={() => openDocument(doc.id)}
        >
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-base">{doc.name}</CardTitle>
              <Badge variant={doc.type === 'file' ? 'default' : 'secondary'}>
                {doc.type === 'file' ? 'File' : 'URL'}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="pt-0">
            <CardDescription className="text-gray-600 text-sm">
              Added on {new Date(doc.uploadedAt).toLocaleDateString()}
            </CardDescription>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default DocumentList;
