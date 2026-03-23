export default function Attributions({ visible }) {
  if (!visible) return null;

  const imageAttributions = [
    {
      image: <img src="/favicon.png" alt="Favicon logo" className="w-8 h-8" />,
      credit: (
        <a
          href="https://www.flaticon.com/free-icons/visualization"
          title="visualization icons"
          className="text-blue-400 hover:text-blue-300 underline"
          target="_blank"
          rel="noopener noreferrer"
        >
          Visualization icons created by juicy_fish - Flaticon
        </a>
      ),
    },
  ];

  return (
    <div className="bg-slate-700 text-white px-8 py-4">
      <h3 className="text-lg font-semibold mb-2">Image Attributions</h3>
      <ul className="space-y-2 text-sm">
        {imageAttributions.map((attr, i) => (
          <li key={i} className="flex items-center gap-3">
            {attr.image}
            {attr.credit}
          </li>
        ))}
      </ul>
    </div>
  );
}
