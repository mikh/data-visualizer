import {
  inferColumnType,
  inferAllColumnTypes,
  computeColumnStats,
} from "../columnUtils";

// ─── inferColumnType ────────────────────────────────────────────────────────

describe("inferColumnType", () => {
  it("returns 'numeric' for integer columns", () => {
    const rows = [["1"], ["2"], ["3"]];
    expect(inferColumnType(rows, 0)).toBe("numeric");
  });

  it("returns 'numeric' for float columns", () => {
    const rows = [["1.5"], ["2.3"], ["3.14"]];
    expect(inferColumnType(rows, 0)).toBe("numeric");
  });

  it("returns 'numeric' for negative numbers", () => {
    const rows = [["-1"], ["0"], ["-3.5"]];
    expect(inferColumnType(rows, 0)).toBe("numeric");
  });

  it("returns 'numeric' for scientific notation", () => {
    const rows = [["1e3"], ["2.5e-4"], ["3E10"]];
    expect(inferColumnType(rows, 0)).toBe("numeric");
  });

  it("returns 'date' for ISO date strings", () => {
    const rows = [["2024-01-01"], ["2024-06-15"], ["2024-12-31"]];
    expect(inferColumnType(rows, 0)).toBe("date");
  });

  it("returns 'date' for date-time strings", () => {
    const rows = [
      ["2024-01-01T10:00:00"],
      ["2024-06-15T12:30:00"],
      ["2024-12-31T23:59:59"],
    ];
    expect(inferColumnType(rows, 0)).toBe("date");
  });

  it("returns 'categorical' for text columns", () => {
    const rows = [["cat"], ["dog"], ["bird"]];
    expect(inferColumnType(rows, 0)).toBe("categorical");
  });

  it("returns 'categorical' for mixed numeric and text", () => {
    const rows = [["1"], ["two"], ["3"]];
    expect(inferColumnType(rows, 0)).toBe("categorical");
  });

  it("returns 'categorical' for all-empty columns", () => {
    const rows = [[""], [null], [undefined]];
    expect(inferColumnType(rows, 0)).toBe("categorical");
  });

  it("returns 'categorical' for empty rows", () => {
    expect(inferColumnType([], 0)).toBe("categorical");
  });

  it("ignores empty values when determining type", () => {
    const rows = [["1"], [""], ["3"], [null], ["5"]];
    expect(inferColumnType(rows, 0)).toBe("numeric");
  });

  it("samples only the first 100 rows", () => {
    // 100 numeric rows followed by text — should still be numeric
    const numericRows = Array.from({ length: 100 }, (_, i) => [String(i)]);
    const mixedRows = [...numericRows, ["not_a_number"]];
    expect(inferColumnType(mixedRows, 0)).toBe("numeric");
  });

  it("handles multi-column rows and reads correct column index", () => {
    const rows = [
      ["cat", "1", "2024-01-01"],
      ["dog", "2", "2024-06-15"],
    ];
    expect(inferColumnType(rows, 0)).toBe("categorical");
    expect(inferColumnType(rows, 1)).toBe("numeric");
    expect(inferColumnType(rows, 2)).toBe("date");
  });

  it("classifies pure numbers as numeric, not date", () => {
    // Date.parse("123") returns a valid date, but should be numeric
    const rows = [["123"], ["456"], ["789"]];
    expect(inferColumnType(rows, 0)).toBe("numeric");
  });
});

// ─── inferAllColumnTypes ────────────────────────────────────────────────────

describe("inferAllColumnTypes", () => {
  it("infers types for all columns", () => {
    const headers = ["id", "name", "date"];
    const rows = [
      ["1", "alice", "2024-01-01"],
      ["2", "bob", "2024-06-15"],
    ];
    const result = inferAllColumnTypes(rows, headers);
    expect(result).toEqual([
      { name: "id", index: 0, type: "numeric" },
      { name: "name", index: 1, type: "categorical" },
      { name: "date", index: 2, type: "date" },
    ]);
  });

  it("returns empty array for empty headers", () => {
    expect(inferAllColumnTypes([], [])).toEqual([]);
  });

  it("handles single column", () => {
    const result = inferAllColumnTypes([["42"]], ["value"]);
    expect(result).toEqual([{ name: "value", index: 0, type: "numeric" }]);
  });
});

// ─── computeColumnStats ─────────────────────────────────────────────────────

describe("computeColumnStats", () => {
  describe("numeric columns", () => {
    it("computes min, max, mean for integers", () => {
      const rows = [["10"], ["20"], ["30"]];
      const stats = computeColumnStats(rows, 0, "numeric");
      expect(stats).toEqual({ count: 3, min: 10, max: 30, mean: 20 });
    });

    it("computes stats for floats", () => {
      const rows = [["1.5"], ["2.5"], ["3.5"]];
      const stats = computeColumnStats(rows, 0, "numeric");
      expect(stats.count).toBe(3);
      expect(stats.min).toBe(1.5);
      expect(stats.max).toBe(3.5);
      expect(stats.mean).toBeCloseTo(2.5);
    });

    it("handles negative numbers", () => {
      const rows = [["-5"], ["0"], ["5"]];
      const stats = computeColumnStats(rows, 0, "numeric");
      expect(stats.min).toBe(-5);
      expect(stats.max).toBe(5);
      expect(stats.mean).toBeCloseTo(0);
    });

    it("handles single value", () => {
      const rows = [["42"]];
      const stats = computeColumnStats(rows, 0, "numeric");
      expect(stats).toEqual({ count: 1, min: 42, max: 42, mean: 42 });
    });

    it("skips empty and null values", () => {
      const rows = [["10"], [""], [null], ["30"]];
      const stats = computeColumnStats(rows, 0, "numeric");
      expect(stats.count).toBe(2);
      expect(stats.min).toBe(10);
      expect(stats.max).toBe(30);
    });

    it("returns count 0 when all values are empty", () => {
      const rows = [[""], [null], [undefined]];
      const stats = computeColumnStats(rows, 0, "numeric");
      expect(stats).toEqual({ count: 0 });
    });
  });

  describe("categorical columns", () => {
    it("counts total and unique values", () => {
      const rows = [["cat"], ["dog"], ["cat"], ["bird"]];
      const stats = computeColumnStats(rows, 0, "categorical");
      expect(stats).toEqual({ count: 4, uniqueCount: 3 });
    });

    it("skips empty values", () => {
      const rows = [["cat"], [""], ["cat"], [null]];
      const stats = computeColumnStats(rows, 0, "categorical");
      expect(stats).toEqual({ count: 2, uniqueCount: 1 });
    });
  });

  describe("date columns", () => {
    it("counts total and unique values", () => {
      const rows = [["2024-01-01"], ["2024-01-01"], ["2024-06-15"]];
      const stats = computeColumnStats(rows, 0, "date");
      expect(stats).toEqual({ count: 3, uniqueCount: 2 });
    });
  });

  describe("unknown type", () => {
    it("returns only count", () => {
      const rows = [["a"], ["b"]];
      const stats = computeColumnStats(rows, 0, "unknown");
      expect(stats).toEqual({ count: 2 });
    });
  });
});
