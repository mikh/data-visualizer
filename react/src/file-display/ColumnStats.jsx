import { useState } from "react";

export default function ColumnStats({ columnStats }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [hoveredColumn, setHoveredColumn] = useState(null);

  if (!columnStats || !Array.isArray(columnStats) || columnStats.length === 0) {
    return null;
  }

  // Format the key names for display (convert snake_case to Title Case)
  const formatKey = (key) => {
    return key
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  // Get the columns to display based on data type
  const getColumnsForDataType = (dataType) => {
    if (dataType === "string") {
      return [
        "column_name",
        "data_type",
        "num_rows",
        "num_unique_values",
        "num_null_values",
        "num_empty_values",
      ];
    } else if (dataType === "numeric") {
      return [
        "column_name",
        "data_type",
        "num_rows",
        "num_unique_values",
        "num_null_values",
        "num_zeros_values",
        "std_dev",
        "mean",
        "median",
        "min_value",
        "max_value",
      ];
    }
    // Default: show all columns
    return Object.keys(columnStats[0] || {});
  };

  // Get all unique columns across all stats (for table headers)
  const getAllColumns = () => {
    const allColumns = new Set();
    columnStats.forEach((stat) => {
      const columns = getColumnsForDataType(stat.data_type);
      columns.forEach((col) => allColumns.add(col));
    });
    return Array.from(allColumns);
  };

  const allColumns = getAllColumns();

  const highlightColumns = new Set(["num_null_values", "num_zeros_values", "num_empty_values"]);

  const getCellHighlight = (column, value, stat) => {
    if (!highlightColumns.has(column) || !value || !stat.num_rows) return "";
    const pct = value / stat.num_rows;
    if (pct <= 0) return "";
    if (pct <= 0.1) return "bg-yellow-100";
    if (pct <= 0.25) return "bg-yellow-200";
    if (pct <= 0.5) return "bg-orange-200";
    if (pct <= 0.75) return "bg-orange-300";
    return "bg-red-200";
  };

  // Format value for display
  const formatValue = (value) => {
    if (value === null || value === undefined) {
      return "—";
    }
    if (typeof value === "number") {
      // Format numbers with appropriate precision
      if (Number.isInteger(value)) {
        return value.toLocaleString();
      }
      // For decimal numbers, show up to 4 decimal places
      return value.toFixed(4).replace(/\.?0+$/, "");
    }
    return String(value);
  };

  return (
    <div className="w-full max-w-6xl mt-6 mx-auto border border-slate-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
      >
        <span>Column Statistics</span>
        <span className="text-slate-400">{isExpanded ? "−" : "+"}</span>
      </button>

      {isExpanded && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead className="sticky top-0 bg-slate-100">
              <tr>
                {allColumns.map((column) => (
                  <th
                    key={column}
                    onMouseEnter={() => setHoveredColumn(column)}
                    onMouseLeave={() => setHoveredColumn(null)}
                    className={`px-3 py-2 text-left text-xs font-medium text-slate-500 border-b border-slate-200 whitespace-nowrap ${
                      column === "column_name"
                        ? "sticky left-0 z-10 bg-slate-100 border-r border-slate-200"
                        : ""
                    }`}
                    style={
                      hoveredColumn === column && column !== "column_name"
                        ? { boxShadow: "inset 0 0 0 9999px rgba(226, 232, 240, 0.5)" }
                        : undefined
                    }
                  >
                    {formatKey(column)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {columnStats.map((stat, rowIndex) => {
                const enabledColumns = getColumnsForDataType(stat.data_type);
                return (
                  <tr
                    key={stat.column_name || rowIndex}
                    className="hover:bg-slate-50 border-b border-slate-100 group"
                  >
                    {allColumns.map((column) => {
                      const isEnabled = enabledColumns.includes(column);
                      const value = stat[column];
                      const highlight = isEnabled ? getCellHighlight(column, value, stat) : "";
                      return (
                        <td
                          key={column}
                          onMouseEnter={() => setHoveredColumn(column)}
                          onMouseLeave={() => setHoveredColumn(null)}
                          className={`px-3 py-1.5 text-xs border-b border-slate-100 ${
                            isEnabled
                              ? `text-slate-700 ${highlight}`
                              : "text-slate-300 bg-slate-50"
                          } whitespace-nowrap ${
                            column === "column_name"
                              ? "sticky left-0 z-10 border-r border-slate-200 bg-white group-hover:bg-slate-50"
                              : ""
                          }`}
                          style={
                            hoveredColumn === column && column !== "column_name"
                              ? { boxShadow: "inset 0 0 0 9999px rgba(226, 232, 240, 0.5)" }
                              : undefined
                          }
                          title={
                            !isEnabled
                              ? `Not applicable for ${stat.data_type} type`
                              : undefined
                          }
                        >
                          {isEnabled ? formatValue(value) : "—"}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
