import { useState } from "react";

export default function ColumnStats({ columnStats }) {
  const [isExpanded, setIsExpanded] = useState(true);

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
    <div className="w-full max-w-6xl mt-6 mx-auto">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-t-lg transition-colors"
      >
        <h2 className="text-lg font-semibold">Column Statistics</h2>
        <span className="text-xl">{isExpanded ? "−" : "+"}</span>
      </button>

      {isExpanded && (
        <div className="border border-gray-300 rounded-b-lg overflow-x-auto">
          <table className="w-full min-w-full">
            <thead>
              <tr className="bg-gray-100">
                {allColumns.map((column) => (
                  <th
                    key={column}
                    className="text-left px-4 py-3 font-semibold text-gray-700 border-b whitespace-nowrap"
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
                    className={`${
                      rowIndex % 2 === 0 ? "bg-white" : "bg-gray-50"
                    } hover:bg-green-100 transition-colors`}
                  >
                    {allColumns.map((column) => {
                      const isEnabled = enabledColumns.includes(column);
                      const value = stat[column];
                      return (
                        <td
                          key={column}
                          className={`px-4 py-3 border-b border-gray-200 ${
                            isEnabled
                              ? "text-gray-600"
                              : "text-gray-300 bg-gray-100"
                          } whitespace-nowrap`}
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
