import GraphPanel from "./graph/GraphPanel";

export default function DataViewer({ loadedFile }) {
  if (!loadedFile) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-400 text-sm">
        Select a CSV file to view its data
      </div>
    );
  }

  const data = loadedFile.data;
  if (!data || !Array.isArray(data) || data.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-slate-400 text-sm">
        No data found in file
      </div>
    );
  }

  const headers = data[0];
  const rows = data.slice(1);

  return (
    <div className="flex-1 flex flex-col gap-4 p-4 overflow-auto">
      <GraphPanel rows={rows} headers={headers} />
    </div>
  );
}
