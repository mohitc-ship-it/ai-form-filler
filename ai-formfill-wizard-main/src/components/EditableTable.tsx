import { useState } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Edit2, Check, X } from "lucide-react";
import { Card } from "@/components/ui/card";

interface TableData {
  headers: string[];
  rows: string[][];
}

interface EditableTableProps {
  title: string;
  data: TableData;
  source: string;
  explanation: string;
  onUpdate: (updatedData: TableData) => void;
}

export const EditableTable = ({ title, data, source, explanation, onUpdate }: EditableTableProps) => {
  const [editingCell, setEditingCell] = useState<{ row: number; col: number } | null>(null);
  const [editValue, setEditValue] = useState("");
  const [tableData, setTableData] = useState(data);

  const startEdit = (rowIndex: number, colIndex: number) => {
    setEditingCell({ row: rowIndex, col: colIndex });
    setEditValue(tableData.rows[rowIndex][colIndex]);
  };

  const saveEdit = () => {
    if (editingCell) {
      const newRows = [...tableData.rows];
      newRows[editingCell.row][editingCell.col] = editValue;
      const updatedData = { ...tableData, rows: newRows };
      setTableData(updatedData);
      onUpdate(updatedData);
      setEditingCell(null);
    }
  };

  const cancelEdit = () => {
    setEditingCell(null);
    setEditValue("");
  };

  return (
    <Card className="p-5 hover:shadow-lg transition-shadow">
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
          <div className="bg-muted/50 rounded-md p-3 mb-3">
            <p className="text-xs font-medium text-muted-foreground mb-1">AI Explanation</p>
            <p className="text-sm text-foreground">{explanation}</p>
          </div>
        </div>

        <div className="border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50">
                {tableData.headers.map((header, index) => (
                  <TableHead key={index} className="font-semibold text-foreground">
                    {header}
                  </TableHead>
                ))}
                <TableHead className="w-20">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tableData.rows.map((row, rowIndex) => (
                <TableRow key={rowIndex} className="hover:bg-muted/30">
                  {row.map((cell, colIndex) => (
                    <TableCell key={colIndex} className="relative">
                      {editingCell?.row === rowIndex && editingCell?.col === colIndex ? (
                        <div className="flex gap-2 items-center">
                          <Input
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            className="h-8"
                            autoFocus
                            onKeyDown={(e) => {
                              if (e.key === "Enter") saveEdit();
                              if (e.key === "Escape") cancelEdit();
                            }}
                          />
                          <div className="flex gap-1">
                            <Button size="icon" variant="ghost" className="h-8 w-8" onClick={saveEdit}>
                              <Check className="w-4 h-4 text-primary" />
                            </Button>
                            <Button size="icon" variant="ghost" className="h-8 w-8" onClick={cancelEdit}>
                              <X className="w-4 h-4 text-muted-foreground" />
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center justify-between group">
                          <span className="text-sm">{cell}</span>
                          <Button
                            size="icon"
                            variant="ghost"
                            className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                            onClick={() => startEdit(rowIndex, colIndex)}
                          >
                            <Edit2 className="w-3 h-3" />
                          </Button>
                        </div>
                      )}
                    </TableCell>
                  ))}
                  <TableCell>
                    <span className="text-xs text-muted-foreground">{rowIndex + 1}</span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground pt-2 border-t">
          <span className="font-medium">Source:</span>
          <span className="truncate">{source}</span>
        </div>
      </div>
    </Card>
  );
};
