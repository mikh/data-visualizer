#!/bin/bash

set -eo pipefail

cd /app

export DATA_FILE_DIR="/data/files"
export LOG_DIR="/data/logs"
export DB_PATH="/data/metadata.sqlite"
export VERSION_FILE="/app/version"

mkdir -p $DATA_FILE_DIR
mkdir -p $LOG_DIR

if [ ! -f $DB_PATH ]; then
  python -m db.db_control \
    --db-path $DB_PATH \
    --data-file-dir $DATA_FILE_DIR \
    create
fi

python run.py --debug --port 8080 --host 0.0.0.0

echo "Flask runner exited."
