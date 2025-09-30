#!/bin/bash

set -eo pipefail

function help {
    echo "Data Visualizer Launcher"
    echo "Usage: run-all.sh [options]"
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

test_flag=""
if [ "$test" = true ]; then
    test_flag="--test"
fi

session_name=$(tmux new -dP "./flask/run-local.sh $test_flag; sleep 99d")
tmux split-window -t "$session_name" -dh "./react/run-local.sh; sleep 99d"
tmux attach -t "$session_name"