/**
 * Transforms CSV data into reaviz-compatible data shapes.
 *
 * reaviz data shapes:
 *   ChartShallowDataShape: { key, data, metadata? }
 *   ChartNestedDataShape:  { key, data: ChartShallowDataShape[], metadata? }
 */

function colIndex(headers, name) {
  return headers.indexOf(name);
}

function parseNumeric(v) {
  if (v == null || v === "") return null;
  const n = Number(v);
  return isNaN(n) ? null : n;
}

function parseDate(v) {
  if (v == null || v === "") return null;
  const d = new Date(v);
  return isNaN(d.getTime()) ? null : d;
}

function parseKey(v, type) {
  if (type === "date") return parseDate(v);
  if (type === "numeric") return parseNumeric(v);
  return v;
}

/**
 * Line chart: single series → ChartShallowDataShape[]
 *             multi series  → ChartNestedDataShape[]
 */
export function transformForLineChart(rows, headers, xCol, yCols, xType) {
  const xi = colIndex(headers, xCol);

  if (yCols.length === 1) {
    const yi = colIndex(headers, yCols[0]);
    return rows
      .map((row, rowIdx) => {
        const key = parseKey(row[xi], xType);
        const data = parseNumeric(row[yi]);
        if (key == null || data == null) return null;
        return { key, data, metadata: { rowIndex: rowIdx } };
      })
      .filter(Boolean);
  }

  // Multi-series → nested
  return yCols.map((yCol) => {
    const yi = colIndex(headers, yCol);
    return {
      key: yCol,
      data: rows
        .map((row, rowIdx) => {
          const key = parseKey(row[xi], xType);
          const data = parseNumeric(row[yi]);
          if (key == null || data == null) return null;
          return { key, data, metadata: { rowIndex: rowIdx } };
        })
        .filter(Boolean),
    };
  });
}

/**
 * Bar chart: ChartShallowDataShape[] with string keys
 */
export function transformForBarChart(rows, headers, xCol, yCol) {
  const xi = colIndex(headers, xCol);
  const yi = colIndex(headers, yCol);

  return rows
    .map((row, rowIdx) => {
      const key = row[xi];
      const data = parseNumeric(row[yi]);
      if (key == null || key === "" || data == null) return null;
      return { key: String(key), data, metadata: { rowIndex: rowIdx } };
    })
    .filter(Boolean);
}

/**
 * Scatter plot: ChartShallowDataShape[] with numeric keys
 */
export function transformForScatterPlot(rows, headers, xCol, yCol) {
  const xi = colIndex(headers, xCol);
  const yi = colIndex(headers, yCol);

  return rows
    .map((row, rowIdx) => {
      const key = parseNumeric(row[xi]);
      const data = parseNumeric(row[yi]);
      if (key == null || data == null) return null;
      return { key, data, metadata: { rowIndex: rowIdx } };
    })
    .filter(Boolean);
}

/**
 * Histogram: ChartShallowDataShape[] (bin ranges as keys, counts as data)
 */
export function transformForHistogram(rows, headers, col, binCount = 20) {
  const ci = colIndex(headers, col);
  const values = [];
  const rowIndicesMap = [];

  rows.forEach((row, rowIdx) => {
    const v = parseNumeric(row[ci]);
    if (v != null) {
      values.push(v);
      rowIndicesMap.push({ value: v, rowIndex: rowIdx });
    }
  });

  if (values.length === 0) return [];

  const min = Math.min(...values);
  const max = Math.max(...values);

  if (min === max) {
    return [
      {
        key: String(min),
        data: values.length,
        metadata: { rowIndices: rowIndicesMap.map((r) => r.rowIndex) },
      },
    ];
  }

  const binWidth = (max - min) / binCount;
  const bins = Array.from({ length: binCount }, (_, i) => ({
    low: min + i * binWidth,
    high: min + (i + 1) * binWidth,
    count: 0,
    rowIndices: [],
  }));

  for (const { value, rowIndex } of rowIndicesMap) {
    let idx = Math.floor((value - min) / binWidth);
    if (idx >= binCount) idx = binCount - 1;
    bins[idx].count++;
    bins[idx].rowIndices.push(rowIndex);
  }

  return bins.map((bin) => ({
    key: `${bin.low.toFixed(1)}-${bin.high.toFixed(1)}`,
    data: bin.count,
    metadata: { rowIndices: bin.rowIndices },
  }));
}

/**
 * Heatmap: ChartNestedDataShape[]
 * Outer key = Y value, inner key = X value, inner data = numeric value
 */
export function transformForHeatmap(rows, headers, xCol, yCol, valueCol) {
  const xi = colIndex(headers, xCol);
  const yi = colIndex(headers, yCol);
  const vi = colIndex(headers, valueCol);

  // Group by Y value
  const grouped = {};
  rows.forEach((row, rowIdx) => {
    const yKey = row[yi];
    const xKey = row[xi];
    const value = parseNumeric(row[vi]);
    if (yKey == null || xKey == null || value == null) return;

    const yStr = String(yKey);
    if (!grouped[yStr]) grouped[yStr] = [];
    grouped[yStr].push({
      key: String(xKey),
      data: value,
      metadata: { rowIndex: rowIdx },
    });
  });

  return Object.entries(grouped).map(([key, data]) => ({ key, data }));
}

/**
 * Area chart: same transforms as line chart
 */
export function transformForAreaChart(rows, headers, xCol, yCols, xType) {
  return transformForLineChart(rows, headers, xCol, yCols, xType);
}
