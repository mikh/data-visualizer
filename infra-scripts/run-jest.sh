#!/bin/bash

set -eo pipefail

function help {
    echo "Runs Jest tests."
    echo ""
    echo "Syntax: run-jest"
    echo "Options:"
    echo "  --log-dir               <dir>                    : Directory to write to."
}

log_dir="tmp/logs/jest"

while [ $# -gt 0 ]; do
    case "$1" in
        --help|-h)
            help
            exit 0
            ;;
        --log-dir)
            log_dir="$2"
            shift;;
        *)
            echo "Unknown argument: $1"
            help
            exit 1
            ;;
    esac
    shift
done

mkdir -p "$log_dir"
cd react
npm install
npm test | tee "../$log_dir/jest.log"
