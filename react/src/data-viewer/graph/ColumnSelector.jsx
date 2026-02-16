import { useMemo } from "react";
import { inferAllColumnTypes } from "../columnUtils";

const COLUMN_CONFIG = {
  line: [
    { key: "x", label: "X Axis", types: ["numeric", "date"], multi: false },
    { key: "y", label: "Y Axis", types: ["numeric"], multi: true },
  ],
  bar: [
    { key: "x", label: "X Axis", types: ["categorical"], multi: false },
    { key: "y", label: "Y Axis", types: ["numeric"], multi: false },
  ],
  scatter: [
    { key: "x", label: "X Axis", types: ["numeric"], multi: false },
    { key: "y", label: "Y Axis", types: ["numeric"], multi: false },
  ],
  histogram: [
    { key: "column", label: "Column", types: ["numeric"], multi: false },
  ],
  heatmap: [
    { key: "x", label: "X Axis", types: ["categorical"], multi: false },
    { key: "y", label: "Y Axis", types: ["categorical"], multi: false },
    { key: "value", label: "Value", types: ["numeric"], multi: false },
  ],
  area: [
    { key: "x", label: "X Axis", types: ["numeric", "date"], multi: false },
    { key: "y", label: "Y Axis", types: ["numeric"], multi: true },
  ],
};

export default function ColumnSelector({
  graphType,
  rows,
  headers,
  selectedColumns,
  onColumnsChange,
}) {
  const columnTypes = useMemo(
    () => inferAllColumnTypes(rows, headers),
    [rows, headers]
  );

  const config = COLUMN_CONFIG[graphType];
  if (!config) return null;

  const handleSingleChange = (key, value) => {
    onColumnsChange({ ...selectedColumns, [key]: value });
  };

  const handleMultiToggle = (key, value) => {
    const current = selectedColumns[key] || [];
    const next = current.includes(value)
      ? current.filter((v) => v !== value)
      : [...current, value];
    onColumnsChange({ ...selectedColumns, [key]: next });
  };

  return (
    <div className="flex flex-wrap gap-4">
      {config.map((field) => {
        const eligible = columnTypes.filter((col) =>
          field.types.includes(col.type)
        );

        if (field.multi) {
          return (
            <div key={field.key}>
              <label className="block text-xs font-medium text-slate-600 mb-1">
                {field.label}
              </label>
              <div className="flex flex-wrap gap-1">
                {eligible.length === 0 && (
                  <span className="text-xs text-slate-400">
                    No {field.types.join("/")} columns
                  </span>
                )}
                {eligible.map((col) => {
                  const checked = (selectedColumns[field.key] || []).includes(
                    col.name
                  );
                  return (
                    <label
                      key={col.name}
                      className={`inline-flex items-center gap-1 px-2 py-1 text-xs rounded border cursor-pointer transition-colors ${
                        checked
                          ? "bg-slate-800 text-white border-slate-800"
                          : "bg-white text-slate-700 border-slate-300 hover:bg-slate-100"
                      }`}
                    >
                      <input
                        type="checkbox"
                        className="sr-only"
                        checked={checked}
                        onChange={() => handleMultiToggle(field.key, col.name)}
                      />
                      {col.name}
                    </label>
                  );
                })}
              </div>
            </div>
          );
        }

        return (
          <div key={field.key}>
            <label className="block text-xs font-medium text-slate-600 mb-1">
              {field.label}
            </label>
            <select
              className="border border-slate-300 rounded px-2 py-1 text-sm bg-white text-slate-700"
              value={selectedColumns[field.key] || ""}
              onChange={(e) => handleSingleChange(field.key, e.target.value)}
            >
              <option value="">Select column</option>
              {eligible.map((col) => (
                <option key={col.name} value={col.name}>
                  {col.name}
                </option>
              ))}
            </select>
          </div>
        );
      })}
    </div>
  );
}
