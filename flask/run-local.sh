#!/bin/bash

set -eo pipefail

function help {
    echo "Flask Runner"
    echo "Usage: run-flask.sh [options]"
    echo "Options:"
    echo "  -h | --help | -help    : Show this help message and exit."
    echo "  --test                 : Run in test mode."
}

test=false

while [ $# -gt 0 ]; do
    case "$1" in
        -h | --help | -help)
            help
            exit;;
        --test)
            test=true
            ;;
        *)
            echo "Error: Invalid Option: $1"
            help
            exit 1;;
    esac
    shift
done

. .venv/bin/activate

cd flask

export FILE_BASE_DIR="untracked/data"
export LOG_DIR="untracked/logs"
export DB_PATH="untracked/metadata.sqlite"
export VERSION_FILE="version"

mkdir -p $FILE_BASE_DIR
mkdir -p $LOG_DIR

if [ "$test" = true ]; then
    db_seed_file="tests/testdata/baseline-db.json"
    data_seed_dir="tests/testdata/baseline"
else
    db_seed_file="tests/testdata/baseline-db.json"
    data_seed_dir="tests/testdata/baseline"
fi

python -m db.db_control  \
    --db-path "$DB_PATH" \
    --data-file-dir "$FILE_BASE_DIR" \
    create \
    --delete-existing \
    --db-seed-data "$db_seed_file" \
    --data-seed-dir "$data_seed_dir"

python run.py

echo "Flask runner exited."