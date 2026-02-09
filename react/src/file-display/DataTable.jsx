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
    <div className="w-full max-w-6xl mt-6 mx-auto">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between bg-purple-600 hover:bg-purple-700 text-white px-4 py-3 rounded-t-lg transition-colors"
      >
        <h2 className="text-lg font-semibold">
          Raw Data ({totalRows} rows)
        </h2>
        <span className="text-xl">{isExpanded ? "−" : "+"}</span>
      </button>

      {isExpanded && (
        <div className="border border-gray-300 rounded-b-lg">
          <div className="overflow-x-auto">
            <table className="w-full min-w-full">
              <thead>
                <tr className="bg-gray-100">
                  {headers.map((header, i) => (
                    <th
                      key={i}
                      className={`text-left px-4 py-3 font-semibold text-gray-700 border-b whitespace-nowrap ${
                        i === 0
                          ? "sticky left-0 z-10 bg-gray-100 border-r border-gray-300"
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
                    className={`${
                      rowIndex % 2 === 0 ? "bg-white" : "bg-gray-50"
                    } hover:bg-purple-100 transition-colors group`}
                  >
                    {headers.map((_, colIndex) => (
                      <td
                        key={colIndex}
                        className={`px-4 py-3 border-b border-gray-200 text-gray-600 whitespace-nowrap ${
                          colIndex === 0
                            ? `sticky left-0 z-10 border-r border-gray-300 ${
                                rowIndex % 2 === 0 ? "bg-white" : "bg-gray-50"
                              } group-hover:bg-purple-100`
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

          <div className="px-4 py-3 text-sm text-gray-500 border-t border-gray-200 flex items-center justify-between">
            <span>
              Showing {rows.length} of {totalRows} rows
            </span>
            {visibleRows < totalRows && (
              <div className="flex gap-2">
                {[10, 30, 50].map((n) => (
                  <button
                    key={n}
                    onClick={() => setVisibleRows((v) => v + n)}
                    className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded transition-colors text-sm"
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
