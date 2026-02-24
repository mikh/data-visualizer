const GRAPH_TYPES = [
  { id: "line", label: "Line Chart" },
  { id: "bar", label: "Bar Chart" },
  { id: "scatter", label: "Scatter Plot" },
  { id: "histogram", label: "Histogram" },
  { id: "heatmap", label: "Heatmap" },
  { id: "area", label: "Area Chart" },
];

export default function GraphTypeSelector({ selected, onSelect }) {
  return (
    <div className="flex flex-wrap gap-2">
      {GRAPH_TYPES.map((type) => (
        <button
          key={type.id}
          onClick={() => onSelect(type.id)}
          className={`px-3 py-1.5 text-sm rounded-md border transition-colors ${
            selected === type.id
              ? "bg-slate-800 text-white border-slate-800"
              : "bg-white text-slate-700 border-slate-300 hover:bg-slate-100"
          }`}
        >
          {type.label}
        </button>
      ))}
    </div>
  );
}
