import { useState } from "react";
import ColumnStats from "./ColumnStats";

export default function FileStats({ fileStats }) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!fileStats) {
    return null;
  }

  // Filter out properties we want to exclude
  const excludedKeys = ["column_stats", "path"];
  const statsToDisplay = Object.entries(fileStats).filter(([key]) => !excludedKeys.includes(key));

  // Format the key names for display (convert snake_case to Title Case)
  const formatKey = (key) => {
    return key
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  return (
    <div className="w-full mt-6">
      <div className="w-full max-w-2xl mx-auto border border-slate-200 rounded-lg overflow-hidden">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-between bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
        >
          <span>File Statistics</span>
          <span className="text-slate-400">{isExpanded ? "−" : "+"}</span>
        </button>

        {isExpanded && (
          <div className="overflow-hidden">
            <table className="w-full text-sm border-collapse">
              <thead className="sticky top-0 bg-slate-100">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 border-b border-slate-200">
                    Property
                  </th>
                  <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 border-b border-slate-200">
                    Value
                  </th>
                </tr>
              </thead>
              <tbody>
                {statsToDisplay.map(([key, value]) => (
                  <tr key={key} className="hover:bg-slate-50 border-b border-slate-100">
                    <td className="px-3 py-1.5 text-xs font-medium text-slate-600 whitespace-nowrap">
                      {formatKey(key)}
                    </td>
                    <td className="px-3 py-1.5 text-xs text-slate-700 whitespace-nowrap">
                      {value}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Display column statistics if they exist */}
      {fileStats.column_stats && <ColumnStats columnStats={fileStats.column_stats} />}
    </div>
  );
}
