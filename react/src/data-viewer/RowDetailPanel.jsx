export default function RowDetailPanel({ row, headers, onClose }) {
  if (row == null) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/20 z-40" onClick={onClose} />

      {/* Panel */}
      <div className="fixed top-0 right-0 h-full w-96 max-w-full bg-white shadow-xl z-50 flex flex-col transform transition-transform duration-200 translate-x-0">
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
          <h3 className="text-sm font-semibold text-slate-800">Row Details</h3>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 text-lg leading-none"
          >
            &times;
          </button>
        </div>
        <div className="flex-1 overflow-auto p-4">
          <table className="w-full text-sm">
            <tbody>
              {headers.map((header, i) => (
                <tr key={i} className="border-b border-slate-100">
                  <td className="py-2 pr-3 font-medium text-slate-600 whitespace-nowrap align-top">
                    {header}
                  </td>
                  <td className="py-2 text-slate-800 break-all">
                    {row[i] ?? <span className="text-slate-300">empty</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
