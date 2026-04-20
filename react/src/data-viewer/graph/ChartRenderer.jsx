import { useMemo } from "react";
import {
  BarChart,
  BarSeries,
  Bar,
  LineChart,
  LineSeries,
  AreaChart,
  AreaSeries,
  PointSeries,
  ScatterPlot,
  ScatterSeries,
  ScatterPoint,
  Heatmap,
  HeatmapSeries,
  HeatmapCell,
  LinearXAxis,
  LinearYAxis,
  LinearXAxisTickSeries,
  LinearXAxisTickLabel,
} from "reaviz";
import { inferColumnType } from "../columnUtils";
import {
  transformForLineChart,
  transformForBarChart,
  transformForScatterPlot,
  transformForHistogram,
  transformForHeatmap,
  transformForAreaChart,
} from "./dataTransformers";

function hasRequiredColumns(graphType, selectedColumns) {
  switch (graphType) {
    case "line":
    case "area":
      return selectedColumns.x && selectedColumns.y && selectedColumns.y.length > 0;
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

export default function ChartRenderer({ graphType, selectedColumns, rows, headers, onRowSelect }) {
  const chartData = useMemo(() => {
    if (!hasRequiredColumns(graphType, selectedColumns)) return null;

    switch (graphType) {
      case "line": {
        const xType = inferColumnType(rows, headers.indexOf(selectedColumns.x));
        return transformForLineChart(rows, headers, selectedColumns.x, selectedColumns.y, xType);
      }
      case "bar":
        return transformForBarChart(rows, headers, selectedColumns.x, selectedColumns.y);
      case "scatter":
        return transformForScatterPlot(rows, headers, selectedColumns.x, selectedColumns.y);
      case "histogram":
        return transformForHistogram(rows, headers, selectedColumns.column);
      case "heatmap":
        return transformForHeatmap(
          rows,
          headers,
          selectedColumns.x,
          selectedColumns.y,
          selectedColumns.value
        );
      case "area": {
        const xType = inferColumnType(rows, headers.indexOf(selectedColumns.x));
        return transformForAreaChart(rows, headers, selectedColumns.x, selectedColumns.y, xType);
      }
      default:
        return null;
    }
  }, [graphType, selectedColumns, rows, headers]);

  if (!chartData || chartData.length === 0) {
    if (!hasRequiredColumns(graphType, selectedColumns)) {
      return (
        <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
          Select the required columns to render a chart
        </div>
      );
    }
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-sm">
        No valid data points for the selected columns
      </div>
    );
  }

  const handleBarClick = ({ value }) => {
    const rowIndex = value?.metadata?.rowIndex;
    if (rowIndex != null) onRowSelect(rowIndex);
  };

  const handlePointClick = (data) => {
    const rowIndex = data?.metadata?.rowIndex;
    if (rowIndex != null) onRowSelect(rowIndex);
  };

  const handleHeatmapClick = (event) => {
    const rowIndex = event?.value?.metadata?.rowIndex ?? event?.metadata?.rowIndex;
    if (rowIndex != null) onRowSelect(rowIndex);
  };

  const handleHistogramBarClick = ({ value }) => {
    const rowIndices = value?.metadata?.rowIndices;
    if (rowIndices && rowIndices.length > 0) onRowSelect(rowIndices[0]);
  };

  const xType = selectedColumns.x
    ? inferColumnType(rows, headers.indexOf(selectedColumns.x))
    : "numeric";
  const xAxisType = xType === "date" ? "time" : xType === "numeric" ? "value" : "category";

  switch (graphType) {
    case "line":
      return (
        <div className="h-80">
          <LineChart
            height={320}
            data={chartData}
            xAxis={<LinearXAxis type={xAxisType} />}
            yAxis={<LinearYAxis type="value" />}
            series={
              <LineSeries
                symbols={
                  <PointSeries show="hover" point={<ScatterPoint onClick={handlePointClick} />} />
                }
              />
            }
          />
        </div>
      );

    case "bar":
      return (
        <div className="h-80">
          <BarChart
            height={320}
            data={chartData}
            xAxis={
              <LinearXAxis
                type="category"
                tickSeries={
                  <LinearXAxisTickSeries label={<LinearXAxisTickLabel rotation={-45} />} />
                }
              />
            }
            yAxis={<LinearYAxis type="value" />}
            series={<BarSeries bar={<Bar onClick={handleBarClick} />} />}
          />
        </div>
      );

    case "scatter":
      return (
        <div className="h-80">
          <ScatterPlot
            height={320}
            data={chartData}
            xAxis={<LinearXAxis type="value" />}
            yAxis={<LinearYAxis type="value" />}
            series={<ScatterSeries point={<ScatterPoint onClick={handlePointClick} />} />}
          />
        </div>
      );

    case "histogram":
      return (
        <div className="h-80">
          <BarChart
            height={320}
            data={chartData}
            xAxis={
              <LinearXAxis
                type="category"
                tickSeries={
                  <LinearXAxisTickSeries label={<LinearXAxisTickLabel rotation={-45} />} />
                }
              />
            }
            yAxis={<LinearYAxis type="value" />}
            series={<BarSeries bar={<Bar onClick={handleHistogramBarClick} />} />}
          />
        </div>
      );

    case "heatmap":
      return (
        <div className="h-80">
          <Heatmap
            height={320}
            data={chartData}
            xAxis={<LinearXAxis type="category" />}
            yAxis={<LinearYAxis type="category" />}
            series={
              <HeatmapSeries
                cell={
                  <HeatmapCell
                    onClick={handleHeatmapClick}
                    onMouseEnter={() => {}}
                    onMouseLeave={() => {}}
                  />
                }
              />
            }
          />
        </div>
      );

    case "area":
      return (
        <div className="h-80">
          <AreaChart
            height={320}
            data={chartData}
            xAxis={<LinearXAxis type={xAxisType} />}
            yAxis={<LinearYAxis type="value" />}
            series={
              <AreaSeries
                symbols={
                  <PointSeries show="hover" point={<ScatterPoint onClick={handlePointClick} />} />
                }
              />
            }
          />
        </div>
      );

    default:
      return null;
  }
}
