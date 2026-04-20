// Tests for pure utility functions extracted from ColumnStats component.
// These are re-declared here since they are defined inside the component scope.

// ─── formatKey ──────────────────────────────────────────────────────────────

function formatKey(key) {
  return key
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

describe("formatKey", () => {
  it("converts snake_case to Title Case", () => {
    expect(formatKey("num_null_values")).toBe("Num Null Values");
  });

  it("handles single word", () => {
    expect(formatKey("mean")).toBe("Mean");
  });

  it("handles already capitalized words", () => {
    expect(formatKey("data_type")).toBe("Data Type");
  });

  it("handles column_name", () => {
    expect(formatKey("column_name")).toBe("Column Name");
  });
});

// ─── getColumnsForDataType ──────────────────────────────────────────────────

function getColumnsForDataType(dataType) {
  if (dataType === "string") {
    return [
      "column_name",
      "data_type",
      "num_rows",
      "num_unique_values",
      "num_null_values",
      "num_empty_values",
    ];
  } else if (dataType === "numeric") {
    return [
      "column_name",
      "data_type",
      "num_rows",
      "num_unique_values",
      "num_null_values",
      "num_zeros_values",
      "std_dev",
      "mean",
      "median",
      "min_value",
      "max_value",
    ];
  }
  return [];
}

describe("getColumnsForDataType", () => {
  it("returns string-specific columns for string type", () => {
    const cols = getColumnsForDataType("string");
    expect(cols).toContain("num_empty_values");
    expect(cols).not.toContain("mean");
    expect(cols).not.toContain("std_dev");
  });

  it("returns numeric-specific columns for numeric type", () => {
    const cols = getColumnsForDataType("numeric");
    expect(cols).toContain("mean");
    expect(cols).toContain("std_dev");
    expect(cols).toContain("min_value");
    expect(cols).toContain("max_value");
    expect(cols).not.toContain("num_empty_values");
  });

  it("always includes common columns", () => {
    for (const type of ["string", "numeric"]) {
      const cols = getColumnsForDataType(type);
      expect(cols).toContain("column_name");
      expect(cols).toContain("data_type");
      expect(cols).toContain("num_rows");
    }
  });

  it("returns empty array for unknown type", () => {
    expect(getColumnsForDataType("boolean")).toEqual([]);
  });
});

// ─── getCellHighlight ───────────────────────────────────────────────────────

const highlightColumns = new Set(["num_null_values", "num_zeros_values", "num_empty_values"]);

function getCellHighlight(column, value, stat) {
  if (!highlightColumns.has(column) || !value || !stat.num_rows) return "";
  const pct = value / stat.num_rows;
  if (pct <= 0) return "";
  if (pct <= 0.1) return "bg-yellow-100";
  if (pct <= 0.25) return "bg-yellow-200";
  if (pct <= 0.5) return "bg-orange-200";
  if (pct <= 0.75) return "bg-orange-300";
  return "bg-red-200";
}

describe("getCellHighlight", () => {
  const stat = { num_rows: 100 };

  it("returns empty for non-highlight columns", () => {
    expect(getCellHighlight("mean", 50, stat)).toBe("");
    expect(getCellHighlight("column_name", 50, stat)).toBe("");
  });

  it("returns empty for zero value", () => {
    expect(getCellHighlight("num_null_values", 0, stat)).toBe("");
  });

  it("returns empty when num_rows is 0", () => {
    expect(getCellHighlight("num_null_values", 5, { num_rows: 0 })).toBe("");
  });

  it("returns yellow-100 for <= 10%", () => {
    expect(getCellHighlight("num_null_values", 10, stat)).toBe("bg-yellow-100");
    expect(getCellHighlight("num_null_values", 5, stat)).toBe("bg-yellow-100");
  });

  it("returns yellow-200 for <= 25%", () => {
    expect(getCellHighlight("num_null_values", 25, stat)).toBe("bg-yellow-200");
    expect(getCellHighlight("num_null_values", 15, stat)).toBe("bg-yellow-200");
  });

  it("returns orange-200 for <= 50%", () => {
    expect(getCellHighlight("num_null_values", 50, stat)).toBe("bg-orange-200");
    expect(getCellHighlight("num_null_values", 30, stat)).toBe("bg-orange-200");
  });

  it("returns orange-300 for <= 75%", () => {
    expect(getCellHighlight("num_zeros_values", 75, stat)).toBe("bg-orange-300");
    expect(getCellHighlight("num_zeros_values", 60, stat)).toBe("bg-orange-300");
  });

  it("returns red-200 for > 75%", () => {
    expect(getCellHighlight("num_empty_values", 80, stat)).toBe("bg-red-200");
    expect(getCellHighlight("num_empty_values", 100, stat)).toBe("bg-red-200");
  });

  it("works for all three highlight column types", () => {
    for (const col of ["num_null_values", "num_zeros_values", "num_empty_values"]) {
      expect(getCellHighlight(col, 5, stat)).toBe("bg-yellow-100");
    }
  });
});
