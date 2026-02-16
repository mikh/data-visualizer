import { useState } from "react";

export default function RawDataTable({ rows, headers }) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="w-full flex items-center justify-between bg-slate-50 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-100 transition-colors"
      >
        <span>Raw Data</span>
        <span className="text-slate-400">{collapsed ? "+" : "\u2212"}</span>
      </button>
      {!collapsed && (
        <div className="max-h-80 overflow-auto">
          <table className="w-full text-sm border-collapse">
            <thead className="sticky top-0 bg-slate-100">
              <tr>
                <th className="px-3 py-2 text-left text-xs font-medium text-slate-500 border-b border-slate-200">
                  #
                </th>
                {headers.map((h, i) => (
                  <th
                    key={i}
                    className="px-3 py-2 text-left text-xs font-medium text-slate-500 border-b border-slate-200 whitespace-nowrap"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIdx) => (
                <tr
                  key={rowIdx}
                  className="hover:bg-slate-50 border-b border-slate-100"
                >
                  <td className="px-3 py-1.5 text-xs text-slate-400">
                    {rowIdx + 1}
                  </td>
                  {headers.map((_, colIdx) => (
                    <td
                      key={colIdx}
                      className="px-3 py-1.5 text-xs text-slate-700 whitespace-nowrap"
                    >
                      {row[colIdx] ?? ""}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
