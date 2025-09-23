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

if [ "$test" = true ]; then
    session_name=$(tmux new -dP "./infra-scripts/run-flask.sh --test")
else
    session_name=$(tmux new -dP "./infra-scripts/run-flask.sh")
fi
tmux split-window -t "$session_name" -dh "./infra-scripts/run-react.sh"
tmux attach -t "$session_name"