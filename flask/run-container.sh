#!/bin/bash

set -eo pipefail

cd /app

export FILE_BASE_DIR="/data/files"
export LOG_DIR="/data/logs"
export DB_PATH="/data/metadata.sqlite"
export VERSION_FILE="/app/version"

mkdir -p $FILE_BASE_DIR
mkdir -p $LOG_DIR

if [ ! -f $DB_PATH ]; then
    python -m db.db_control \
        --db-path $DB_PATH \
        --data-file-dir $FILE_BASE_DIR \
        create
fi

python run.py

echo "Flask runner exited."