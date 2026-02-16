import { useMemo } from "react";
import StatsPanel from "./StatsPanel";
import RawDataTable from "./RawDataTable";
import GraphPanel from "./graph/GraphPanel";

export default function DataViewer({ loadedFile }) {
  const { headers, rows } = useMemo(() => {
    if (!loadedFile || !loadedFile.data || loadedFile.data.length === 0) {
      return { headers: [], rows: [] };
    }
    const data = loadedFile.data;
    return {
      headers: data[0],
      rows: data.slice(1),
    };
  }, [loadedFile]);

  if (!loadedFile) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-400 text-sm">
        Select a CSV file to view its data
      </div>
    );
  }

  if (headers.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-400 text-sm">
        No data found in file
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col gap-4 p-4 overflow-auto">
      <StatsPanel rows={rows} headers={headers} />
      <RawDataTable rows={rows} headers={headers} />
      <GraphPanel rows={rows} headers={headers} />
    </div>
  );
}
