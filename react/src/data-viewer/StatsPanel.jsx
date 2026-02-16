import { inferAllColumnTypes, computeColumnStats } from "./columnUtils";
import { useMemo } from "react";

export default function StatsPanel({ rows, headers }) {
  const columns = useMemo(() => {
    const types = inferAllColumnTypes(rows, headers);
    return types.map((col) => ({
      ...col,
      stats: computeColumnStats(rows, col.index, col.type),
    }));
  }, [rows, headers]);

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
      <h3 className="text-sm font-semibold text-slate-700 mb-2">
        Dataset Summary
      </h3>
      <div className="text-xs text-slate-500 mb-3">
        {rows.length} rows &middot; {headers.length} columns
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
        {columns.map((col) => (
          <div
            key={col.index}
            className="bg-white border border-slate-200 rounded px-3 py-2"
          >
            <div className="font-medium text-sm text-slate-800 truncate">
              {col.name}
            </div>
            <div className="text-xs text-slate-400 mb-1">{col.type}</div>
            {col.type === "numeric" && col.stats.count > 0 && (
              <div className="text-xs text-slate-600 space-x-2">
                <span>min: {col.stats.min.toFixed(2)}</span>
                <span>max: {col.stats.max.toFixed(2)}</span>
                <span>mean: {col.stats.mean.toFixed(2)}</span>
              </div>
            )}
            {(col.type === "categorical" || col.type === "date") && (
              <div className="text-xs text-slate-600">
                {col.stats.uniqueCount} unique values
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
