import { useState } from "react";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, Copy, Download, Edit, ThumbsDown, ThumbsUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { useToast } from "@/components/ui/use-toast";

interface ContentArtifactProps {
  content: string;
  platform: string;
  contentType: string;
  onEdit?: (content: string) => void;
  onSave?: (content: string) => void;
  className?: string;
}

export function ContentArtifact({
  content,
  platform,
  contentType,
  onEdit,
  onSave,
  className,
}: ContentArtifactProps) {
  const { toast } = useToast();
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    toast({
      title: "Copied to clipboard",
      description: "Content has been copied to your clipboard",
    });
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([content], { type: "text/plain" });
    element.href = URL.createObjectURL(file);
    element.download = `${contentType}-${platform}-${new Date().toISOString().split("T")[0]}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
    
    toast({
      title: "Downloaded",
      description: "Content has been downloaded as a text file",
    });
  };

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-lg">Generated Content</CardTitle>
        <div className="flex gap-2">
          <Badge variant="outline">{platform}</Badge>
          <Badge variant="outline">{contentType}</Badge>
        </div>
      </CardHeader>
      <CardContent className="pt-2">
        <div className="whitespace-pre-wrap rounded-md bg-muted p-4 text-sm">
          {content}
        </div>
      </CardContent>
      <CardFooter className="flex justify-between border-t pt-4">
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => onEdit?.(content)}>
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </Button>
          <Button variant="outline" size="sm" onClick={handleCopy}>
            {copied ? (
              <Check className="mr-2 h-4 w-4" />
            ) : (
              <Copy className="mr-2 h-4 w-4" />
            )}
            {copied ? "Copied" : "Copy"}
          </Button>
          <Button variant="outline" size="sm" onClick={handleDownload}>
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="icon" className="h-8 w-8">
            <ThumbsUp className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" className="h-8 w-8">
            <ThumbsDown className="h-4 w-4" />
          </Button>
          {onSave && (
            <Button size="sm" onClick={() => onSave(content)}>
              Save as Draft
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  );
}
