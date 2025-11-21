#!/bin/bash

set -eo pipefail

function help {
    echo "Run Pytests & Coverage"
    echo "Usage: run-pytests.sh [options]"
    echo "Options:"
    echo "  -h | --help | -help    : Show this help message and exit."
    echo "  --output-dir           : Output directory for the coverage report."
    echo "  --omit                 : Omit files for coverage report."
    echo "  --min-passing-coverage  : Minimum passing coverage percentage."
}

output_dir="untracked/tests/pytests"
omit="db_control.py,logging_helper.py"
min_passing_coverage=80

while [ $# -gt 0 ]; do
    case "$1" in
        -h | --help | -help)
            help
            exit;;
        --output-dir)
            output_dir="$2"
            shift;;
        --omit)
            omit="$2"
            shift;;
        --min-passing-coverage)
            min_passing_coverage="$2"
            shift;;
        *)
            echo "Error: Invalid Option: $1"
            help
            exit 1;;
    esac
    shift
done


cd flask
mkdir -p $output_dir
export FILE_BASE_DIR="untracked/data"
export LOG_DIR="untracked/logs"
export DB_PATH="untracked/metadata.sqlite"
export TESTDATA_DIR="tests/testdata"
export TEST_DATA_FILE_DIR="untracked/tests/data"
export TEST_DB_JSON_PATH="tests/testdata/baseline-db.json"
export VERSION_FILE="version"

coverage run \
    --source="." \
    --omit="$omit" \
    --data-file="$output_dir/.coverage" \
    -m pytest

coverage html \
    --data-file="$output_dir/.coverage" \
    --directory="$output_dir/html"

printf "\n\nREPORT:\n\n"
coverage report \
    -m \
    --data-file "$output_dir/.coverage" \
    | tee "$output_dir/coverage.log"
printf "\n\nRESULT:\n\n"

total=$(coverage report --format=total --data-file "$output_dir/.coverage")
if ((total < min_passing_coverage)); then
    echo "Total coverage (${total}%) is less than minimum passing coverage (${min_passing_coverage}%)"
    exit 1
fi

echo "Total coverage (${total}%) passes minimum passing coverage requirements (${min_passing_coverage}%)"
