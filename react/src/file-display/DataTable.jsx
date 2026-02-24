import { useState } from "react";

const INITIAL_ROWS = 10;

export default function DataTable({ data }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [visibleRows, setVisibleRows] = useState(INITIAL_ROWS);

  if (!data || !Array.isArray(data) || data.length < 2) {
    return null;
  }

  const headers = data[0];
  const totalRows = data.length - 1;
  const rows = data.slice(1, visibleRows + 1);

  return (
    <div className="w-full max-w-6xl mt-6 mx-auto border border-slate-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
      >
        <span>Raw Data ({totalRows} rows)</span>
        <span className="text-slate-400">{isExpanded ? "−" : "+"}</span>
      </button>

      {isExpanded && (
        <div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead className="sticky top-0 bg-slate-100">
                <tr>
                  {headers.map((header, i) => (
                    <th
                      key={i}
                      className={`px-3 py-2 text-left text-xs font-medium text-slate-500 border-b border-slate-200 whitespace-nowrap ${
                        i === 0
                          ? "sticky left-0 z-10 bg-slate-100 border-r border-slate-200"
                          : ""
                      }`}
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, rowIndex) => (
                  <tr
                    key={rowIndex}
                    className="hover:bg-slate-50 border-b border-slate-100 group"
                  >
                    {headers.map((_, colIndex) => (
                      <td
                        key={colIndex}
                        className={`px-3 py-1.5 text-xs text-slate-700 whitespace-nowrap ${
                          colIndex === 0
                            ? "sticky left-0 z-10 border-r border-slate-200 bg-white group-hover:bg-slate-50"
                            : ""
                        }`}
                      >
                        {row[colIndex] !== null && row[colIndex] !== undefined
                          ? String(row[colIndex])
                          : "—"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="px-3 py-2 text-xs text-slate-500 border-t border-slate-200 flex items-center justify-between">
            <span>
              Showing {rows.length} of {totalRows} rows
            </span>
            {visibleRows < totalRows && (
              <div className="flex gap-2">
                {[10, 30, 50].map((n) => (
                  <button
                    key={n}
                    onClick={() => setVisibleRows((v) => v + n)}
                    className="px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded transition-colors text-xs border border-slate-200"
                  >
                    +{n} rows
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
