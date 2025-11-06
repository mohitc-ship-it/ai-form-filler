import { Upload, X, FileText } from "lucide-react";
import { useState, useCallback } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { cn } from "@/lib/utils";

interface FileUploadZoneProps {
  title: string;
  description: string;
  allowMultiple?: boolean;
  showCheckboxes?: boolean;
  onFilesChange: (files: File[]) => void;
  selectedFiles?: Set<string>;
  onFileSelect?: (fileName: string, selected: boolean) => void;
}

export const FileUploadZone = ({
  title,
  description,
  allowMultiple = true,
  showCheckboxes = false,
  onFilesChange,
  selectedFiles,
  onFileSelect,
}: FileUploadZoneProps) => {
  const [files, setFiles] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);

      const droppedFiles = Array.from(e.dataTransfer.files);
      const newFiles = allowMultiple ? [...files, ...droppedFiles] : droppedFiles.slice(0, 1);
      setFiles(newFiles);
      onFilesChange(newFiles);
    },
    [files, allowMultiple, onFilesChange]
  );

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      const newFiles = allowMultiple ? [...files, ...selectedFiles] : selectedFiles.slice(0, 1);
      setFiles(newFiles);
      onFilesChange(newFiles);
    }
  };

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index);
    setFiles(newFiles);
    onFilesChange(newFiles);
  };

  return (
    <div className="flex flex-col h-full gap-4">
      <div>
        <h2 className="text-xl font-semibold text-foreground mb-1">{title}</h2>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>

      <div
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        className={cn(
          "relative flex-1 border-2 border-dashed rounded-lg transition-all overflow-hidden",
          isDragging
            ? "border-primary bg-primary/5 scale-[1.02]"
            : "border-border hover:border-primary/50 hover:bg-muted/30"
        )}
      >
        {files.length === 0 ? (
          <>
            <input
              type="file"
              multiple={allowMultiple}
              onChange={handleFileInput}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
              accept=".pdf,.docx,.xlsx,.xls,.doc,.txt"
            />
            <div className="flex flex-col items-center justify-center h-full p-8 text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Upload className="w-8 h-8 text-primary" />
              </div>
              <p className="text-sm font-medium text-foreground mb-1">
                Drop files here or click to upload
              </p>
              <p className="text-xs text-muted-foreground">
                PDF, DOCX, XLSX, XLS, DOC, TXT
              </p>
            </div>
          </>
        ) : (
          <div className="relative h-full">
            <div className="p-4 space-y-2 overflow-y-auto h-full">
              {files.map((file, index) => (
                <Card key={index} className="relative p-3 flex items-center gap-3 hover:shadow-md transition-shadow z-20">
                  <FileText className="w-5 h-5 text-primary flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">
                      {file.name}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  {showCheckboxes && onFileSelect && (
                    <Checkbox
                      checked={selectedFiles?.has(file.name) || false}
                      onCheckedChange={(checked) =>
                        onFileSelect(file.name, checked as boolean)
                      }
                      className="z-30"
                    />
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      removeFile(index);
                    }}
                    className="flex-shrink-0 z-30 hover:bg-destructive/10 hover:text-destructive"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </Card>
              ))}
            </div>
            <div className="absolute bottom-4 left-4 right-4 z-20">
              <label className="block">
                <input
                  type="file"
                  multiple={allowMultiple}
                  onChange={handleFileInput}
                  className="hidden"
                  accept=".pdf,.docx,.xlsx,.xls,.doc,.txt"
                />
                <Button variant="outline" className="w-full gap-2" asChild>
                  <span className="cursor-pointer">
                    <Upload className="w-4 h-4" />
                    Add More Files
                  </span>
                </Button>
              </label>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
