import { useState, useCallback } from "react";
import GraphTypeSelector from "./GraphTypeSelector";
import ColumnSelector from "./ColumnSelector";
import ChartRenderer from "./ChartRenderer";
import RowDetailPanel from "../RowDetailPanel";

export default function GraphPanel({ rows, headers }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [selectedGraphType, setSelectedGraphType] = useState(null);
  const [selectedColumns, setSelectedColumns] = useState({});
  const [selectedRowIndex, setSelectedRowIndex] = useState(null);

  const handleGraphTypeChange = useCallback((type) => {
    setSelectedGraphType(type);
    setSelectedColumns({});
    setSelectedRowIndex(null);
  }, []);

  const handleRowSelect = useCallback((rowIndex) => {
    setSelectedRowIndex(rowIndex);
  }, []);

  const handleCloseDetail = useCallback(() => {
    setSelectedRowIndex(null);
  }, []);

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
      >
        <span>Visualization</span>
        <span className="text-slate-400">{isExpanded ? "−" : "+"}</span>
      </button>

      {isExpanded && (
        <div className="p-4 space-y-4">
          <GraphTypeSelector
            selected={selectedGraphType}
            onSelect={handleGraphTypeChange}
          />

          {selectedGraphType && (
            <ColumnSelector
              graphType={selectedGraphType}
              rows={rows}
              headers={headers}
              selectedColumns={selectedColumns}
              onColumnsChange={setSelectedColumns}
            />
          )}

          {selectedGraphType && (
            <ChartRenderer
              graphType={selectedGraphType}
              selectedColumns={selectedColumns}
              rows={rows}
              headers={headers}
              onRowSelect={handleRowSelect}
            />
          )}

          <RowDetailPanel
            row={selectedRowIndex != null ? rows[selectedRowIndex] : null}
            headers={headers}
            onClose={handleCloseDetail}
          />
        </div>
      )}
    </div>
  );
}
