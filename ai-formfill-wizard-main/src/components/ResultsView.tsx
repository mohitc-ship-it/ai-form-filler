import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Download, Edit2, Check, ExternalLink } from "lucide-react";
import { toast } from "sonner"; 
import { EditableTable } from "./EditableTable";

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

interface ResultsViewProps {
  results: Result[];
  onExport: (updatedResults: Result[]) => void;
}

export const ResultsView = ({ results, onExport }: ResultsViewProps) => {
  const [editedResults, setEditedResults] = useState<Result[]>(results);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [editValue, setEditValue] = useState("");

  const startEditing = (index: number, result: Result) => {
    if ("value" in result) {
      setEditingIndex(index);
      setEditValue(result.value);
    }
  };

  const saveEdit = (index: number) => {
    const updated = [...editedResults];
    const result = updated[index];
    if ("value" in result) {
      updated[index] = { ...result, value: editValue };
    }
    setEditedResults(updated);
    setEditingIndex(null);
    toast.success("Value updated");
  };

  const updateTable = (index: number, updatedData: { headers: string[]; rows: string[][] }) => {
    const updated = [...editedResults];
    const result = updated[index];
    if ("type" in result && result.type === "table") {
      updated[index] = { ...result, data: updatedData };
      setEditedResults(updated);
      toast.success("Table updated");
    }
  };

  const handleExport = () => {
    onExport(editedResults);
    toast.success("Exporting documents...");
  };

  return (
    <div className="flex flex-col h-full gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-foreground mb-1">
            AI Results
          </h2>
          <p className="text-sm text-muted-foreground">
            Review and edit filled values
          </p>
        </div>
        <Button onClick={handleExport} className="gap-2">
          <Download className="w-4 h-4" />
          Export Documents
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4">
        {editedResults.map((result, index) => {
          if ("type" in result && result.type === "table") {
            return (
              <EditableTable
                key={index}
                title={result.title}
                data={result.data}
                source={result.source}
                explanation={result.explanation}
                onUpdate={(updatedData) => updateTable(index, updatedData)}
              />
            );
          }

          const fieldResult = result as FieldResult;
          return (
            <Card key={index} className="p-5 hover:shadow-lg transition-shadow">
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-semibold text-foreground mb-2">
                      {fieldResult.field}
                    </h3>
                    
                    {editingIndex === index ? (
                      <div className="flex gap-2">
                        <Input
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          className="flex-1"
                          autoFocus
                        />
                        <Button
                          size="icon"
                          onClick={() => saveEdit(index)}
                          variant="default"
                        >
                          <Check className="w-4 h-4" />
                        </Button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <p className="text-base font-medium text-primary flex-1">
                          {fieldResult.value}
                        </p>
                        <Button
                          size="icon"
                          variant="ghost"
                          onClick={() => startEditing(index, fieldResult)}
                        >
                          <Edit2 className="w-4 h-4" />
                        </Button>
                      </div>
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="bg-muted/50 rounded-md p-3">
                    <p className="text-xs font-medium text-muted-foreground mb-1">
                      AI Explanation
                    </p>
                    <p className="text-sm text-foreground">{fieldResult.explanation}</p>
                  </div>

                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <ExternalLink className="w-3 h-3" />
                    <span className="font-medium">Source:</span>
                    <span className="truncate">{fieldResult.source}</span>
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
