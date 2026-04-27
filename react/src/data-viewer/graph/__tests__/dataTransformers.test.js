import {
  transformForLineChart,
  transformForBarChart,
  transformForScatterPlot,
  transformForHistogram,
  transformForHeatmap,
  transformForAreaChart,
} from "../dataTransformers";

// ─── transformForLineChart ──────────────────────────────────────────────────

describe("transformForLineChart", () => {
  const headers = ["x", "y1", "y2"];

  describe("single series", () => {
    it("returns shallow data shape with numeric x", () => {
      const rows = [
        ["1", "10", ""],
        ["2", "20", ""],
        ["3", "30", ""],
      ];
      const result = transformForLineChart(rows, headers, "x", ["y1"], "numeric");
      expect(result).toEqual([
        { key: 1, data: 10, metadata: { rowIndex: 0 } },
        { key: 2, data: 20, metadata: { rowIndex: 1 } },
        { key: 3, data: 30, metadata: { rowIndex: 2 } },
      ]);
    });

    it("returns shallow data shape with date x", () => {
      const rows = [["2024-01-01", "10", ""]];
      const result = transformForLineChart(rows, headers, "x", ["y1"], "date");
      expect(result).toHaveLength(1);
      expect(result[0].key).toBeInstanceOf(Date);
      expect(result[0].data).toBe(10);
    });

    it("filters out rows with null x or y", () => {
      const rows = [
        ["1", "10", ""],
        ["", "20", ""], // null x
        ["3", "", ""], // null y
        ["4", "abc", ""], // non-numeric y
      ];
      const result = transformForLineChart(rows, headers, "x", ["y1"], "numeric");
      expect(result).toHaveLength(1);
      expect(result[0].key).toBe(1);
    });

    it("returns empty array when all data is invalid", () => {
      const rows = [
        ["", "", ""],
        [null, null, ""],
      ];
      const result = transformForLineChart(rows, headers, "x", ["y1"], "numeric");
      expect(result).toEqual([]);
    });
  });

  describe("multi series", () => {
    it("returns nested data shape", () => {
      const rows = [
        ["1", "10", "100"],
        ["2", "20", "200"],
      ];
      const result = transformForLineChart(rows, headers, "x", ["y1", "y2"], "numeric");
      expect(result).toHaveLength(2);
      expect(result[0].key).toBe("y1");
      expect(result[0].data).toHaveLength(2);
      expect(result[1].key).toBe("y2");
      expect(result[1].data).toHaveLength(2);
    });

    it("each series filters independently", () => {
      const rows = [
        ["1", "10", ""], // y2 is empty
        ["2", "", "200"], // y1 is empty
      ];
      const result = transformForLineChart(rows, headers, "x", ["y1", "y2"], "numeric");
      expect(result[0].data).toHaveLength(1); // y1 only has row 0
      expect(result[0].data[0].data).toBe(10);
      expect(result[1].data).toHaveLength(1); // y2 only has row 1
      expect(result[1].data[0].data).toBe(200);
    });
  });

  it("preserves rowIndex metadata", () => {
    const rows = [
      ["1", "10", ""],
      ["2", "abc", ""], // filtered out
      ["3", "30", ""],
    ];
    const result = transformForLineChart(rows, headers, "x", ["y1"], "numeric");
    expect(result[0].metadata.rowIndex).toBe(0);
    expect(result[1].metadata.rowIndex).toBe(2);
  });

  it("uses categorical x as-is", () => {
    const rows = [["cat", "10", ""]];
    const result = transformForLineChart(rows, headers, "x", ["y1"], "categorical");
    expect(result[0].key).toBe("cat");
  });
});

// ─── transformForBarChart ───────────────────────────────────────────────────

describe("transformForBarChart", () => {
  const headers = ["category", "value"];

  it("returns one entry per unique x value", () => {
    const rows = [
      ["a", "10"],
      ["b", "20"],
      ["c", "30"],
    ];
    const result = transformForBarChart(rows, headers, "category", "value");
    expect(result).toEqual([
      { key: "a", data: 10, metadata: { rowIndex: 0 } },
      { key: "b", data: 20, metadata: { rowIndex: 1 } },
      { key: "c", data: 30, metadata: { rowIndex: 2 } },
    ]);
  });

  it("sums duplicate x values", () => {
    const rows = [
      ["a", "10"],
      ["a", "20"],
      ["b", "5"],
    ];
    const result = transformForBarChart(rows, headers, "category", "value");
    expect(result).toHaveLength(2);
    expect(result[0]).toEqual({ key: "a", data: 30, metadata: { rowIndex: 0 } });
    expect(result[1]).toEqual({ key: "b", data: 5, metadata: { rowIndex: 2 } });
  });

  it("tracks firstRowIndex for duplicates", () => {
    const rows = [
      ["x", "1"],
      ["x", "2"],
    ];
    const result = transformForBarChart(rows, headers, "category", "value");
    // firstRowIndex should be 0 (the first occurrence)
    expect(result[0].metadata.rowIndex).toBe(0);
  });

  it("filters out rows with empty x or non-numeric y", () => {
    const rows = [
      ["", "10"], // empty x
      ["a", "abc"], // non-numeric y
      ["b", ""], // empty y
      ["c", "30"], // valid
    ];
    const result = transformForBarChart(rows, headers, "category", "value");
    expect(result).toHaveLength(1);
    expect(result[0].key).toBe("c");
  });

  it("returns empty array when no valid data", () => {
    const rows = [
      ["", ""],
      [null, null],
    ];
    const result = transformForBarChart(rows, headers, "category", "value");
    expect(result).toEqual([]);
  });
});

// ─── transformForScatterPlot ────────────────────────────────────────────────

describe("transformForScatterPlot", () => {
  const headers = ["x", "y"];

  it("returns numeric key-data pairs", () => {
    const rows = [
      ["1", "10"],
      ["2", "20"],
    ];
    const result = transformForScatterPlot(rows, headers, "x", "y");
    expect(result).toEqual([
      { key: 1, data: 10, metadata: { rowIndex: 0 } },
      { key: 2, data: 20, metadata: { rowIndex: 1 } },
    ]);
  });

  it("filters non-numeric values", () => {
    const rows = [
      ["1", "10"],
      ["abc", "20"],
      ["3", "xyz"],
    ];
    const result = transformForScatterPlot(rows, headers, "x", "y");
    expect(result).toHaveLength(1);
    expect(result[0].key).toBe(1);
  });

  it("handles zero values", () => {
    const rows = [["0", "0"]];
    const result = transformForScatterPlot(rows, headers, "x", "y");
    expect(result).toEqual([{ key: 0, data: 0, metadata: { rowIndex: 0 } }]);
  });

  it("handles negative values", () => {
    const rows = [["-5", "-10"]];
    const result = transformForScatterPlot(rows, headers, "x", "y");
    expect(result[0].key).toBe(-5);
    expect(result[0].data).toBe(-10);
  });

  it("returns empty array for all-invalid data", () => {
    const rows = [["abc", "def"]];
    const result = transformForScatterPlot(rows, headers, "x", "y");
    expect(result).toEqual([]);
  });
});

// ─── transformForHistogram ──────────────────────────────────────────────────

describe("transformForHistogram", () => {
  const headers = ["value"];

  it("creates bins from numeric values", () => {
    const rows = Array.from({ length: 20 }, (_, i) => [String(i)]);
    const result = transformForHistogram(rows, headers, "value", 5);
    expect(result).toHaveLength(5);
    // All bins should have counts that sum to 20
    const totalCount = result.reduce((sum, bin) => sum + bin.data, 0);
    expect(totalCount).toBe(20);
  });

  it("returns empty array for no valid values", () => {
    const rows = [["abc"], [""], [null]];
    const result = transformForHistogram(rows, headers, "value");
    expect(result).toEqual([]);
  });

  it("handles single unique value (min === max)", () => {
    const rows = [["5"], ["5"], ["5"]];
    const result = transformForHistogram(rows, headers, "value");
    expect(result).toHaveLength(1);
    expect(result[0].key).toBe("5");
    expect(result[0].data).toBe(3);
    expect(result[0].metadata.rowIndices).toEqual([0, 1, 2]);
  });

  it("assigns max value to last bin", () => {
    const rows = [["0"], ["10"]];
    const result = transformForHistogram(rows, headers, "value", 2);
    // value 10 should be in the last bin, not overflow
    const totalCount = result.reduce((sum, bin) => sum + bin.data, 0);
    expect(totalCount).toBe(2);
  });

  it("tracks rowIndices per bin", () => {
    const rows = [["1"], ["2"], ["3"]];
    const result = transformForHistogram(rows, headers, "value", 1);
    expect(result).toHaveLength(1);
    expect(result[0].metadata.rowIndices).toEqual([0, 1, 2]);
  });

  it("formats bin keys as low-high range", () => {
    const rows = [["0"], ["10"]];
    const result = transformForHistogram(rows, headers, "value", 2);
    // Each key should be formatted as "low-high"
    result.forEach((bin) => {
      expect(bin.key).toMatch(/^-?\d+\.?\d*--?\d+\.?\d*$/);
    });
  });

  it("defaults to 20 bins", () => {
    // 100 values spread across 0-99
    const rows = Array.from({ length: 100 }, (_, i) => [String(i)]);
    const result = transformForHistogram(rows, headers, "value");
    expect(result).toHaveLength(20);
  });

  it("filters non-numeric values and bins the rest", () => {
    const rows = [["1"], ["abc"], ["3"], [""], ["5"]];
    const result = transformForHistogram(rows, headers, "value", 2);
    const totalCount = result.reduce((sum, bin) => sum + bin.data, 0);
    expect(totalCount).toBe(3); // only 1, 3, 5
  });
});

// ─── transformForHeatmap ────────────────────────────────────────────────────

describe("transformForHeatmap", () => {
  const headers = ["x", "y", "value"];

  it("creates nested data grouped by y then x", () => {
    const rows = [
      ["a", "row1", "10"],
      ["b", "row1", "20"],
      ["a", "row2", "30"],
    ];
    const result = transformForHeatmap(rows, headers, "x", "y", "value");
    expect(result).toHaveLength(2); // 2 y-groups

    const row1 = result.find((r) => r.key === "row1");
    expect(row1.data).toHaveLength(2);
    expect(row1.data.find((d) => d.key === "a").data).toBe(10);
    expect(row1.data.find((d) => d.key === "b").data).toBe(20);

    const row2 = result.find((r) => r.key === "row2");
    expect(row2.data).toHaveLength(1);
    expect(row2.data[0].data).toBe(30);
  });

  it("sums duplicate x/y pairs", () => {
    const rows = [
      ["a", "row1", "10"],
      ["a", "row1", "20"],
    ];
    const result = transformForHeatmap(rows, headers, "x", "y", "value");
    expect(result[0].data[0].data).toBe(30);
  });

  it("tracks firstRowIndex for duplicates", () => {
    const rows = [
      ["a", "row1", "10"],
      ["a", "row1", "20"],
    ];
    const result = transformForHeatmap(rows, headers, "x", "y", "value");
    expect(result[0].data[0].metadata.rowIndex).toBe(0);
  });

  it("filters rows with null keys or non-numeric values", () => {
    const rows = [
      [null, "r1", "10"], // null x
      ["a", null, "20"], // null y
      ["b", "r1", "abc"], // non-numeric value
      ["c", "r1", "30"], // valid
    ];
    const result = transformForHeatmap(rows, headers, "x", "y", "value");
    expect(result).toHaveLength(1);
    expect(result[0].data).toHaveLength(1);
    expect(result[0].data[0].key).toBe("c");
  });

  it("returns empty array for no valid data", () => {
    const rows = [["", "", ""]];
    const result = transformForHeatmap(rows, headers, "x", "y", "value");
    expect(result).toEqual([]);
  });
});

// ─── transformForAreaChart ──────────────────────────────────────────────────

describe("transformForAreaChart", () => {
  it("delegates to transformForLineChart", () => {
    const headers = ["x", "y"];
    const rows = [
      ["1", "10"],
      ["2", "20"],
    ];
    const lineResult = transformForLineChart(rows, headers, "x", ["y"], "numeric");
    const areaResult = transformForAreaChart(rows, headers, "x", ["y"], "numeric");
    expect(areaResult).toEqual(lineResult);
  });
});
