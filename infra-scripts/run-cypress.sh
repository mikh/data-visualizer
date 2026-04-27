#!/bin/bash

set -eo pipefail

function help {
  echo "Cypress Test Runner"
  echo "Usage: run-cypress.sh [options]"
  echo "Options:"
  echo "  -h | --help     : Show this help message and exit."
  echo "  --open          : Open Cypress interactive mode (default: headless run)."
}

mode="run"

while [ $# -gt 0 ]; do
  case "$1" in
    -h | --help | -help)
      help
      exit
      ;;
    --open)
      mode="open"
      ;;
    *)
      echo "Error: Invalid Option: $1"
      help
      exit 1
      ;;
  esac
  shift
done

# shellcheck source=/dev/null
. .venv/bin/activate

# Set up Flask with test data
cd flask

export FILE_BASE_DIR="untracked/tests/cypress-data"
export LOG_DIR="untracked/logs"
export DB_PATH="untracked/tests/cypress-metadata.sqlite"
export VERSION_FILE="version"
export DATA_FILE_DIR="$FILE_BASE_DIR"

mkdir -p "$FILE_BASE_DIR"
mkdir -p "$LOG_DIR"

python -m db.db_control \
  --db-path "$DB_PATH" \
  --data-file-dir "$FILE_BASE_DIR" \
  create \
  --delete-existing \
  --db-seed-data "tests/testdata/baseline-db.json" \
  --data-seed-dir "tests/testdata/baseline"

# Start Flask in background
python run.py --port 5000 --host 127.0.0.1 &
flask_pid=$!

cd ../react

# Start Vite dev server in background
export VITE_URL_PREFIX=http://127.0.0.1:5000
VITE_REACT_VERSION=$(cat version)
export VITE_REACT_VERSION
npx vite --port 5173 --host 127.0.0.1 &
vite_pid=$!

# Wait for both servers to be ready
echo "Waiting for Flask (port 5000)..."
timeout 30 bash -c 'until curl -s http://127.0.0.1:5000/api/version > /dev/null 2>&1; do sleep 0.5; done'
echo "Flask is ready."

echo "Waiting for Vite (port 5173)..."
timeout 30 bash -c 'until curl -s http://127.0.0.1:5173 > /dev/null 2>&1; do sleep 0.5; done'
echo "Vite is ready."

# Run Cypress
if [ "$mode" = "open" ]; then
  npx cypress open
else
  npx cypress run
fi

cypress_exit=$?

# Cleanup
kill $flask_pid 2>/dev/null || true
kill $vite_pid 2>/dev/null || true

exit $cypress_exit
