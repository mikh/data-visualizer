# Data Visualizer

Full-stack web app for uploading, organizing, and visualizing CSV/JSON data files. Built for ML workflows: comparing experiment results, exploring datasets, plotting training curves.

## Architecture

```
Flask backend (Python 3.11) ──► SQLite metadata DB
       │                         (file hierarchy, tags, column stats)
       ├── Serves React frontend as static files (production)
       ├── Stores data files on disk with numeric IDs (1.csv, 2.csv, ...)
       └── Analyzes CSVs on upload via pandas

React frontend (Vite + Tailwind) ──► reaviz charts (D3-based)
       ├── File tree browser (@mikh/file-tree)
       ├── Metadata/stats display
       └── 6 chart types: line, bar, scatter, histogram, heatmap, area
```

**Data flow:** Files uploaded → stored on disk → metadata + computed stats saved to SQLite → frontend fetches tree, loads file data, renders charts.

## Directory Layout

| Path | What it is |
|------|-----------|
| `flask/run.py` | Flask entry point. All API routes defined here |
| `flask/dir_tree_lib.py` | File tree operations (list, upload, delete, move, copy) |
| `flask/db/models.py` | SQLAlchemy models: FileMetadata, Tag, FileStats, ColumnStats |
| `flask/db/db_interface.py` | Database CRUD operations |
| `flask/db/data_interface.py` | Data file I/O (read/write CSV/JSON to disk) |
| `flask/data/csv_analyzer.py` | Pandas-based CSV statistics computation |
| `flask/tests/` | pytest tests + test fixtures in `testdata/` |
| `react/src/App.jsx` | Main React component |
| `react/src/file-manager/` | File tree browser UI + API client (`FileManagerInterface.js`) |
| `react/src/file-display/` | File metadata, stats, tags, raw data table |
| `react/src/data-viewer/` | Chart visualization UI |
| `react/src/data-viewer/graph/` | ChartRenderer, GraphPanel, ColumnSelector, dataTransformers |
| `helm-chart/` | Kubernetes Helm chart for deployment |
| `infra-scripts/` | Build, test, version bump, and local dev scripts |
| `Dockerfile` | Multi-stage build (React build → Flask runtime image) |
| `.drone.yml` | CI/CD pipeline (test → build → push to Harbor) |

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/version` | GET | Backend version |
| `/api/tree` | POST | File tree operations (action in body: `list`, `load`, `delete`, `move`, `copy`, `update`) |
| `/api/upload` | POST | Upload a file (multipart form data) |

The `/api/tree` endpoint is the main workhorse. The `action` field in the POST body determines the operation.

## Database Models

- **FileMetadata** — file/folder entry with `name`, `path` (unique), `data_file_type`, `data_file_path`. Has M2M relationship with Tags, 1:1 with FileStats.
- **Tag** — simple `name` (unique), M2M with FileMetadata.
- **FileStats** — per-file stats: `num_columns`, `num_rows`. Has 1:M relationship with ColumnStats.
- **ColumnStats** — per-column: `data_type`, `mean`, `median`, `std_dev`, `min_value`, `max_value`, `num_zeros_values`, `num_unique_values`, `num_null_values`, `num_empty_values`.

## Frontend Chart Types

| Type | X axis | Y axis | Notes |
|------|--------|--------|-------|
| Line | 1 numeric/date | 1+ numeric | Training curves, time series |
| Bar | 1 categorical/numeric/date | 1 numeric | Comparisons |
| Scatter | 1 numeric | 1 numeric | Correlations |
| Histogram | auto-binned column | count | Distributions |
| Heatmap | 1 col | 1 col | + 1 numeric value col |
| Area | 1 numeric/date | 1+ numeric | Cumulative/stacked |

Column type inference (`columnUtils.js`) samples first 100 rows and classifies columns as `numeric`, `date`, or `categorical`.

## Common Commands

```bash
# Local development (Flask + React in tmux)
./infra-scripts/run-all.sh

# Run backend tests
./infra-scripts/run-pytests.sh
# Or directly:
cd flask && python -m pytest tests/ -v

# Build Docker image
./infra-scripts/build-image.sh

# Version bump
python infra-scripts/version-bump.py [major|minor]

# Deploy via Helm
just deploy
```

## Key Technical Details

- **File storage**: Logical folder hierarchy lives in SQLite; actual files stored flat in `untracked/data/` (or `/data/files` in container) with numeric IDs.
- **CSV analysis** runs on upload: pandas computes per-column descriptive statistics, stored in ColumnStats table.
- **React build** is served as static files by Flask in production. In dev, Vite dev server runs separately.
- **Container** runs Flask on port 8080. Health checks hit `/api/version`.
- **PVC** in Kubernetes stores both the SQLite DB and data files (5Gi default).

## Version

Current: v0.3.6 (tracked in `flask/version`, `react/version`, and `helm-chart/data-visualizer/Chart.yaml`).
