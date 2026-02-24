const SAMPLE_SIZE = 100;

function isNumeric(value) {
  if (value === "" || value == null) return false;
  return !isNaN(Number(value));
}

function isDate(value) {
  if (value === "" || value == null) return false;
  const parsed = Date.parse(value);
  if (isNaN(parsed)) return false;
  // Reject pure numbers that Date.parse accepts (e.g. "123")
  if (isNumeric(value)) return false;
  return true;
}

export function inferColumnType(rows, colIndex) {
  const sample = rows.slice(0, SAMPLE_SIZE);
  const nonEmpty = sample
    .map((row) => row[colIndex])
    .filter((v) => v != null && v !== "");

  if (nonEmpty.length === 0) return "categorical";

  const allNumeric = nonEmpty.every(isNumeric);
  if (allNumeric) return "numeric";

  const allDate = nonEmpty.every(isDate);
  if (allDate) return "date";

  return "categorical";
}

export function inferAllColumnTypes(rows, headers) {
  return headers.map((header, i) => ({
    name: header,
    index: i,
    type: inferColumnType(rows, i),
  }));
}

export function computeColumnStats(rows, colIndex, type) {
  const values = rows
    .map((row) => row[colIndex])
    .filter((v) => v != null && v !== "");

  if (type === "numeric") {
    const nums = values.map(Number).filter((n) => !isNaN(n));
    if (nums.length === 0) return { count: 0 };
    const min = Math.min(...nums);
    const max = Math.max(...nums);
    const mean = nums.reduce((a, b) => a + b, 0) / nums.length;
    return { count: nums.length, min, max, mean };
  }

  if (type === "categorical" || type === "date") {
    const unique = new Set(values);
    return { count: values.length, uniqueCount: unique.size };
  }

  return { count: values.length };
}
