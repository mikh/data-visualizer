export default function TagDisplay({ tags }) {
  // Generate a deterministic color from a string
  const stringToColor = (str) => {
    // Use a better hash function with more bit mixing
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32-bit integer
    }

    // Apply additional bit mixing to spread out similar strings
    const mix = (h) => {
      h ^= h >>> 16;
      h = Math.imul(h, 0x85ebca6b);
      h ^= h >>> 13;
      h = Math.imul(h, 0xc2b2ae35);
      h ^= h >>> 16;
      return h >>> 0; // Convert to unsigned 32-bit integer
    };

    const mixed = mix(hash);

    // Use different parts of the mixed hash for each color component
    const hue = mixed % 360;
    const saturation = 65 + ((mixed >> 8) % 20); // 65-85%
    const lightness = 45 + ((mixed >> 16) % 15); // 45-60%

    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  };

  if (!tags || tags.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-wrap gap-2">
      {tags.map((tag, index) => (
        <span
          key={`${tag}-${index}`}
          className="px-3 py-1 rounded-full text-white text-sm font-medium"
          style={{ backgroundColor: stringToColor(tag) }}
        >
          {tag}
        </span>
      ))}
    </div>
  );
}
