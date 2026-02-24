# Graph Visualization Plan

## Overview

Add interactive graph visualization to the data visualizer frontend. When a CSV file is loaded,
users can create charts from the tabular data by selecting a graph type and the relevant columns.
Clicking a data point on any chart opens a slide-out side panel showing the full row's values.

## Library

**reaviz** — a React data visualization library built on D3.js. It provides composable chart
components with built-in tooltips, animations, and click handlers. It uses the same data shape
conventions across chart types, which simplifies the column-to-chart mapping logic.

Install: `npm i reaviz --save`

## Graph Types

The following graph types cover the most common needs in data analysis and machine learning work:

| Graph Type | Use Cases | Required Columns |
|---|---|---|
| **Line Chart** | Training curves (loss/accuracy over epochs), time series trends, metric tracking over iterations | X: 1 numeric/date column, Y: 1+ numeric columns |
| **Bar Chart** | Feature importance, categorical value comparisons, class distribution counts | X: 1 categorical column, Y: 1 numeric column |
| **Scatter Plot** | Correlation between two variables, cluster visualization, residual plots | X: 1 numeric column, Y: 1 numeric column |
| **Histogram** | Distribution of a single variable, identifying skew/outliers, bin frequency analysis | 1 numeric column (auto-binned) |
| **Heatmap** | Correlation matrices, confusion matrices, parameter sweep results | X: 1 categorical column, Y: 1 categorical column, Value: 1 numeric column |
| **Area Chart** | Cumulative metrics, stacked comparisons across categories, resource usage over time | X: 1 numeric/date column, Y: 1+ numeric columns |

## Architecture

### New Components

```
react/src/
├── file-manager/
│   └── FileManager.jsx          (modify: pass loaded_file down, add layout)
├── data-viewer/
│   ├── DataViewer.jsx            (new: orchestrates stats, table, and graph panel)
│   ├── StatsPanel.jsx            (new: shows column types, row count, basic stats)
│   ├── RawDataTable.jsx          (new: renders CSV data as a table)
│   ├── graph/
│   │   ├── GraphPanel.jsx        (new: graph type selector + column selector + chart)
│   │   ├── GraphTypeSelector.jsx (new: dropdown/buttons to pick chart type)
│   │   ├── ColumnSelector.jsx    (new: column picker, adapts to selected graph type)
│   │   ├── ChartRenderer.jsx     (new: renders the correct reaviz chart)
│   │   └── dataTransformers.js   (new: converts CSV rows to reaviz data shapes)
│   └── RowDetailPanel.jsx        (new: slide-out panel showing a full row)
```

### Data Flow

```
FileManager (loads CSV)
  └─▶ DataViewer (receives loaded file object)
        ├─▶ StatsPanel (column names, types, row count, min/max/mean for numeric cols)
        ├─▶ RawDataTable (scrollable table of the raw CSV data)
        └─▶ GraphPanel
              ├─▶ GraphTypeSelector (user picks: line, bar, scatter, histogram, heatmap, area)
              ├─▶ ColumnSelector (shows appropriate column pickers for the chosen graph type)
              ├─▶ ChartRenderer (transforms data + renders the reaviz chart)
              └─▶ RowDetailPanel (slide-out, shown on data point click)
```

## Implementation Steps

### Step 1: Data Display Foundation

Create the `DataViewer`, `StatsPanel`, and `RawDataTable` components. Modify `FileManager` to
render `DataViewer` when a file is loaded, instead of only logging the data.

**DataViewer.jsx** — receives the loaded file object and lays out the sub-components in a
vertical stack: stats at the top, then a tab or section for raw data, then the graph panel.

**StatsPanel.jsx** — parses the CSV data (array of arrays where row 0 is headers) and displays:
- Number of rows and columns
- For each column: name, inferred type (numeric, categorical, date), and basic stats
  - Numeric: min, max, mean
  - Categorical: unique value count

**RawDataTable.jsx** — renders the CSV as a scrollable HTML table with the header row as `<thead>`
and the data rows as `<tbody>`. Should handle large datasets gracefully (consider virtualizing
rows if performance becomes an issue, but start simple).

### Step 2: Graph Type Selection

Create `GraphPanel.jsx` and `GraphTypeSelector.jsx`.

**GraphTypeSelector.jsx** — displays the six graph types as selectable buttons or a dropdown.
When a type is selected, it notifies the parent so the column selector can update.

**GraphPanel.jsx** — manages the state for:
- `selectedGraphType` (null initially)
- `selectedColumns` (object whose shape depends on graph type)
- `selectedRow` (for the detail panel, null initially)

### Step 3: Column Selection

Create `ColumnSelector.jsx`. This component adapts its UI based on the selected graph type:

| Graph Type | Column Inputs |
|---|---|
| Line Chart | X axis: single column dropdown (numeric/date), Y axis: multi-select checkboxes (numeric only) |
| Bar Chart | X axis: single column dropdown (categorical), Y axis: single column dropdown (numeric) |
| Scatter Plot | X axis: single column dropdown (numeric), Y axis: single column dropdown (numeric) |
| Histogram | Column: single column dropdown (numeric only) |
| Heatmap | X axis: single column dropdown (categorical), Y axis: single column dropdown (categorical), Value: single column dropdown (numeric) |
| Area Chart | X axis: single column dropdown (numeric/date), Y axis: multi-select checkboxes (numeric only) |

Column dropdowns should be filtered by type — the component needs the inferred column types from
the stats analysis. A shared utility function should handle type inference (reusable between
StatsPanel and ColumnSelector).

### Step 4: Data Transformation Layer

Create `dataTransformers.js` with functions that convert CSV row data into reaviz data shapes:

```
transformForLineChart(rows, headers, xCol, yCols)
  → single series: ChartShallowDataShape[]
  → multi series: ChartNestedDataShape[]

transformForBarChart(rows, headers, xCol, yCol)
  → ChartShallowDataShape[] with string keys

transformForScatterPlot(rows, headers, xCol, yCol)
  → ChartShallowDataShape[] with numeric keys

transformForHistogram(rows, headers, col, binCount=20)
  → ChartShallowDataShape[] (bin ranges as keys, counts as data)

transformForHeatmap(rows, headers, xCol, yCol, valueCol)
  → ChartNestedDataShape[] (y-values as outer keys, x-values as inner keys)

transformForAreaChart(rows, headers, xCol, yCols)
  → same as line chart transforms
```

Each transformer should also attach the original row index to the `metadata` field of each data
point, so that click handlers can look up the full row. For histogram, metadata should contain
the list of row indices that fell into that bin.

### Step 5: Chart Rendering

Create `ChartRenderer.jsx`. Based on `selectedGraphType` and `selectedColumns`, it:

1. Calls the appropriate transformer from `dataTransformers.js`
2. Renders the corresponding reaviz chart component
3. Wires up `onClick` handlers on data point elements (Bar, ScatterPoint, HeatmapCell, or
   PointSeries symbols for Line/Area charts) that extract the row index from `metadata` and
   call `onRowSelect(rowIndex)`

Each chart should configure appropriate axis types:
- Line/Area/Scatter: `LinearXAxis type="value"` for numeric, `type="time"` for dates
- Bar: `LinearXAxis type="category"`
- Heatmap: both axes `type="category"`

### Step 6: Row Detail Slide-Out Panel

Create `RowDetailPanel.jsx` — a slide-out panel that appears on the right side of the screen.

Behavior:
- Hidden by default
- When a data point is clicked, it slides in from the right showing all column values for that
  row in a key-value list
- Has a close button to dismiss
- For histograms (which represent binned data), show a list of all rows in the bin, or show the
  first row with navigation arrows

Styling: use Tailwind classes for the slide-out animation (`transform`, `translate-x`,
`transition`). The panel should overlay the content, not push it aside.

### Step 7: Integration and Layout

Update `FileManager.jsx` to render `DataViewer` alongside the file tree. The layout should be:

```
┌──────────────────────────────────────────────────┐
│ Header                                           │
├────────────┬─────────────────────────────────────┤
│ File Tree  │ DataViewer                          │
│            │ ┌─────────────────────────────────┐ │
│            │ │ StatsPanel                      │ │
│            │ ├─────────────────────────────────┤ │
│            │ │ RawDataTable (collapsible)      │ │
│            │ ├─────────────────────────────────┤ │
│            │ │ GraphPanel                      │ │
│            │ │  [Type Selector] [Col Selector] │ │
│            │ │  ┌───────────────────────┐      │ │
│            │ │  │ Chart                 │      │ │
│            │ │  └───────────────────────┘      │ │
│            │ └─────────────────────────────────┘ │
└────────────┴─────────────────────────────────────┘
```

The file tree and data viewer sit side-by-side using a flex or grid layout. The data viewer takes
the remaining horizontal space.

### Step 8: Polish

- Ensure charts resize responsively (reaviz auto-sizes when width/height are omitted)
- Add loading/empty states for when no file is loaded or no graph type is selected
- Handle edge cases: columns with missing values, non-numeric data in numeric columns
- Style consistency with the existing Tailwind theme

## Column Type Inference

A shared utility (`columnUtils.js`) should infer column types from the CSV data:

```javascript
function inferColumnType(rows, colIndex) {
  // Sample up to 100 rows
  // If all non-empty values parse as numbers → "numeric"
  // If all non-empty values parse as dates → "date"
  // Otherwise → "categorical"
}
```

This is used by both `StatsPanel` (to show type info) and `ColumnSelector` (to filter dropdowns).

## reaviz Data Point Click → Row Mapping

Every data transformer attaches `metadata: { rowIndex }` (or `metadata: { rowIndices }` for
histograms) to each data point. The click handlers extract this:

```javascript
// Bar chart example
<BarSeries
  bar={
    <Bar
      onClick={({ value }) => {
        const rowIndex = value.metadata?.rowIndex;
        if (rowIndex != null) onRowSelect(rowIndex);
      }}
    />
  }
/>

// Line/Area chart example (via point symbols)
<LineSeries
  symbols={
    <PointSeries
      point={
        <ScatterPoint
          onClick={(d) => {
            const rowIndex = d.metadata?.rowIndex;
            if (rowIndex != null) onRowSelect(rowIndex);
          }}
        />
      }
    />
  }
/>
```

## File Impact Summary

| File | Change |
|---|---|
| `react/package.json` | Add `reaviz` dependency |
| `react/src/file-manager/FileManager.jsx` | Add side-by-side layout, pass `loaded_file` to DataViewer |
| `react/src/data-viewer/DataViewer.jsx` | New — orchestrator component |
| `react/src/data-viewer/StatsPanel.jsx` | New — file stats display |
| `react/src/data-viewer/RawDataTable.jsx` | New — raw data table |
| `react/src/data-viewer/graph/GraphPanel.jsx` | New — graph section orchestrator |
| `react/src/data-viewer/graph/GraphTypeSelector.jsx` | New — chart type picker |
| `react/src/data-viewer/graph/ColumnSelector.jsx` | New — column picker |
| `react/src/data-viewer/graph/ChartRenderer.jsx` | New — renders reaviz charts |
| `react/src/data-viewer/graph/dataTransformers.js` | New — CSV to reaviz data conversion |
| `react/src/data-viewer/RowDetailPanel.jsx` | New — slide-out row detail panel |
| `react/src/data-viewer/columnUtils.js` | New — column type inference utility |
