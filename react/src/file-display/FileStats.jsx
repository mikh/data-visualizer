import { useState } from "react";

export default function FileStats({ fileStats }) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (!fileStats) {
    return null;
  }

  // Filter out properties we want to exclude
  const excludedKeys = ["column_stats", "path"];
  const statsToDisplay = Object.entries(fileStats).filter(
    ([key]) => !excludedKeys.includes(key)
  );

  // Format the key names for display (convert snake_case to Title Case)
  const formatKey = (key) => {
    return key
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  // TODO: Display columns stats if they exist with highlighting for important stats

  return (
    <div className="w-full max-w-2xl mt-6">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-t-lg transition-colors"
      >
        <h2 className="text-lg font-semibold">File Statistics</h2>
        <span className="text-xl">{isExpanded ? "−" : "+"}</span>
      </button>

      {isExpanded && (
        <div className="border border-gray-300 rounded-b-lg overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-100">
                <th className="text-left px-4 py-3 font-semibold text-gray-700 border-b">
                  Property
                </th>
                <th className="text-left px-4 py-3 font-semibold text-gray-700 border-b">
                  Value
                </th>
              </tr>
            </thead>
            <tbody>
              {statsToDisplay.map(([key, value], index) => (
                <tr
                  key={key}
                  className={`${
                    index % 2 === 0 ? "bg-white" : "bg-gray-50"
                  } hover:bg-blue-100 transition-colors cursor-pointer`}
                >
                  <td className="px-4 py-3 border-b border-gray-200 font-medium text-gray-700">
                    {formatKey(key)}
                  </td>
                  <td className="px-4 py-3 border-b border-gray-200 text-gray-600">
                    {value}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
