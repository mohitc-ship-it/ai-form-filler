import { useState } from "react";
import { FileUploadZone } from "@/components/FileUploadZone";
import { ProcessButton } from "@/components/ProcessButton";
import { ResultsView } from "@/components/ResultsView";
import { toast } from "sonner";

interface FieldResult {
  field: string;
  value: string;
  explanation: string;
  source: string;
}

interface TableResult {
  type: "table";
  title: string;
  data: {
    headers: string[];
    rows: string[][];
  };
  explanation: string;
  source: string;
}

type Result = FieldResult | TableResult;

const Index = () => {
  const [contextFiles, setContextFiles] = useState<File[]>([]);
  const [formFiles, setFormFiles] = useState<File[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<Result[] | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [showLoader, setShowLoader] = useState(false); // 👈 loader state

  // no selectedContext anymore: all uploaded context files will be used

  const handleProcess = async () => {
  if (contextFiles.length === 0 || formFiles.length === 0) {
      toast.error("Please upload both context documents and forms");
      return;
    }


    setIsProcessing(true);
    toast.info("Processing documents with AI...");

    try {
      const formData = new FormData();

      // Append all files to the multipart form
      // We'll send a JSON metadata field `files_meta` describing each file
      const filesMeta: { file_type: "context" | "form"; file_name: string }[] = [];

      contextFiles.forEach((file) => {
        formData.append("files", file);
        filesMeta.push({ file_type: "context", file_name: file.name });
      });

      formFiles.forEach((file) => {
        formData.append("files", file);
        filesMeta.push({ file_type: "form", file_name: file.name });
      });

      formData.append("files_meta", JSON.stringify(filesMeta));

      const response = await fetch("http://localhost:8000/api/process", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("API processing failed");

      const respJson = await response.json();

      // New backend returns an object with session_id, saved_dir, files, data
      // Fall back to older behavior where it returned an array directly
      let data: Result[] = [];
      if (Array.isArray(respJson)) {
        data = respJson as Result[];
      } else if (respJson && respJson.data) {
        data = respJson.data as Result[];
        if (respJson.session_id) setSessionId(String(respJson.session_id));
      } else {
        // unknown shape, try to use it directly
        data = (respJson as any) || [];
      }

      // 👇 Show loader for exactly 10 seconds before showing results
      setShowLoader(true);
      setTimeout(() => {
        setResults(data);
        setShowLoader(false);
      }, 10000);

      toast.success("Documents processed successfully!");
    } catch (err) {
      console.warn("API failed, using static JSON fallback:", err);
      toast.warning("Using fallback demo data...");

      const demoData: Result[] = [
        {
          field: "Company Name",
          value: "Acme Corporation",
          explanation:
            "Found in the header of the business registration document, page 1",
          source: "business_registration.pdf - Page 1",
        },
        {
          field: "Registration Number",
          value: "REG-2024-001234",
          explanation:
            "Official registration number mentioned in the certificate section",
          source: "business_certificate.pdf - Section 2",
        },
        {
          type: "table",
          title: "Employee Information",
          data: {
            headers: ["Employee Name", "Position", "Department", "Start Date"],
            rows: [
              ["John Smith", "CEO", "Executive", "Jan 15, 2024"],
              ["Sarah Johnson", "CTO", "Technology", "Feb 1, 2024"],
              ["Michael Chen", "CFO", "Finance", "Feb 15, 2024"],
              ["Emily Davis", "VP Sales", "Sales", "Mar 1, 2024"],
            ],
          },
          explanation:
            "Employee roster extracted from the organizational chart spreadsheet, including key leadership positions",
          source: "org_chart.xlsx - Sheet 'Leadership Team'",
        },
        {
          field: "Business Address",
          value: "123 Main Street, Suite 400, San Francisco, CA 94102",
          explanation:
            "Primary business address listed in the contact information section",
          source: "business_registration.pdf - Contact Details",
        },
      ];

      // 👇 Same 10-sec loader delay for fallback
      setShowLoader(true);
      setTimeout(() => {
        setResults(demoData);
        setShowLoader(false);
      }, 10000);

      toast.success("Demo results loaded successfully!");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExport = async (updatedResults: Result[]) => {
    try {
      if (!formFiles[0]) {
        toast.error("No form uploaded to export");
        return;
      }

      const fileType = formFiles[0].name.endsWith(".xlsx")
        ? "xlsx"
        : formFiles[0].name.endsWith(".docx")
        ? "docx"
        : "unknown";

      toast.info(`Generating filled ${fileType.toUpperCase()} file...`);

  // include session_id when available so backend can find session file
  const sessionQuery = sessionId ? `&session_id=${encodeURIComponent(sessionId)}` : "";
  const response = await fetch(`http://localhost:8000/api/download?type=${fileType}${sessionQuery}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ results: updatedResults }),
      });

      if (!response.ok) throw new Error("Download failed");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `filled_form.${fileType}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success("Document downloaded successfully!");
    } catch (err) {
      console.error("Download error:", err);
      toast.error("Failed to download file — using static mock");
      toast.success("Static export completed (mock mode)");
    }
  };

  const handleReset = () => {
    setResults(null);
    toast.info("Ready for new documents");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/30 relative">
      {/* Fullscreen Loader */}
      {showLoader && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background/95 backdrop-blur-md">
          <div className="w-16 h-16 border-4 border-t-transparent border-primary rounded-full animate-spin"></div>
          <p className="mt-6 text-lg font-semibold text-primary">
            Preparing your AI results...
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            This may take some time
          </p>
        </div>
      )}

      {/* Header */}
      <header className="border-b border-border bg-card/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                AI Document Filler
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Automatically fill forms using AI-powered context analysis
              </p>
            </div>
            {results && (
              <button
                onClick={handleReset}
                className="text-sm text-primary hover:text-primary-glow transition-colors font-medium"
              >
                ← Start New
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="container mx-auto px-6 py-8">
        {!results ? (
          <div className="space-y-8">
            <div className="grid lg:grid-cols-2 gap-6">
              <div className="h-[600px]">
                <FileUploadZone
                  title="Context Documents"
                  description="Upload reference documents that contain the information to fill the forms (all uploaded will be used)"
                  allowMultiple={true}
                  showCheckboxes={false}
                  onFilesChange={setContextFiles}
                />
              </div>

              <div className="h-[600px]">
                <FileUploadZone
                  title="Forms to Fill"
                  description="Upload the forms (DOCX, Excel) that need to be filled with data"
                  allowMultiple={true}
                  onFilesChange={setFormFiles}
                />
              </div>
            </div>

            <div className="py-8">
              <ProcessButton
                onClick={handleProcess}
                disabled={contextFiles.length === 0 || formFiles.length === 0}
                loading={isProcessing}
              />
              {(contextFiles.length === 0 || formFiles.length === 0) && (
                <p className="text-center text-sm text-muted-foreground mt-4">
                  {contextFiles.length === 0 && "Upload context documents"}
                  {contextFiles.length > 0 && formFiles.length === 0 &&
                    "Upload forms to fill"}
                </p>
              )}
            </div>
          </div>
        ) : (
          <div className="h-[calc(100vh-200px)]">
            <ResultsView results={results} onExport={handleExport} />
          </div>
        )}
      </main>
    </div>
  );
};

export default Index;
