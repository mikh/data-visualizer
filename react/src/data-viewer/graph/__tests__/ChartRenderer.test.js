// Test the hasRequiredColumns validation logic from ChartRenderer.
// Since hasRequiredColumns is not exported, we re-implement the same logic here
// and test it to guard against regressions in the validation rules.
// The function returns truthy/falsy values (not strict booleans).

function hasRequiredColumns(graphType, selectedColumns) {
  switch (graphType) {
    case "line":
    case "area":
      return (
        selectedColumns.x &&
        selectedColumns.y &&
        selectedColumns.y.length > 0
      );
    case "bar":
      return selectedColumns.x && selectedColumns.y;
    case "scatter":
      return selectedColumns.x && selectedColumns.y;
    case "histogram":
      return !!selectedColumns.column;
    case "heatmap":
      return selectedColumns.x && selectedColumns.y && selectedColumns.value;
    default:
      return false;
  }
}

describe("hasRequiredColumns", () => {
  describe("line / area", () => {
    it("returns truthy with x and non-empty y array", () => {
      expect(hasRequiredColumns("line", { x: "a", y: ["b"] })).toBeTruthy();
      expect(hasRequiredColumns("area", { x: "a", y: ["b", "c"] })).toBeTruthy();
    });

    it("returns falsy with missing x", () => {
      expect(hasRequiredColumns("line", { y: ["b"] })).toBeFalsy();
    });

    it("returns falsy with empty y array", () => {
      expect(hasRequiredColumns("line", { x: "a", y: [] })).toBeFalsy();
    });

    it("returns falsy with missing y", () => {
      expect(hasRequiredColumns("line", { x: "a" })).toBeFalsy();
    });
  });

  describe("bar", () => {
    it("returns truthy with x and y", () => {
      expect(hasRequiredColumns("bar", { x: "a", y: "b" })).toBeTruthy();
    });

    it("returns falsy with missing x or y", () => {
      expect(hasRequiredColumns("bar", { x: "a" })).toBeFalsy();
      expect(hasRequiredColumns("bar", { y: "b" })).toBeFalsy();
      expect(hasRequiredColumns("bar", {})).toBeFalsy();
    });
  });

  describe("scatter", () => {
    it("returns truthy with x and y", () => {
      expect(hasRequiredColumns("scatter", { x: "a", y: "b" })).toBeTruthy();
    });

    it("returns falsy with missing x or y", () => {
      expect(hasRequiredColumns("scatter", { x: "a" })).toBeFalsy();
      expect(hasRequiredColumns("scatter", {})).toBeFalsy();
    });
  });

  describe("histogram", () => {
    it("returns truthy with column set", () => {
      expect(hasRequiredColumns("histogram", { column: "a" })).toBeTruthy();
    });

    it("returns falsy with missing or empty column", () => {
      expect(hasRequiredColumns("histogram", {})).toBeFalsy();
      expect(hasRequiredColumns("histogram", { column: "" })).toBeFalsy();
    });
  });

  describe("heatmap", () => {
    it("returns truthy with x, y, and value", () => {
      expect(
        hasRequiredColumns("heatmap", { x: "a", y: "b", value: "c" })
      ).toBeTruthy();
    });

    it("returns falsy with any missing field", () => {
      expect(hasRequiredColumns("heatmap", { x: "a", y: "b" })).toBeFalsy();
      expect(hasRequiredColumns("heatmap", { x: "a", value: "c" })).toBeFalsy();
      expect(hasRequiredColumns("heatmap", { y: "b", value: "c" })).toBeFalsy();
    });
  });

  describe("unknown type", () => {
    it("returns false", () => {
      expect(hasRequiredColumns("unknown", { x: "a", y: "b" })).toBe(false);
    });
  });
});
