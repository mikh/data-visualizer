#!/bin/bash

session_name=$(tmux new -dP "./infra-scripts/run-flask.sh")
tmux split-window -t "$session_name" -dh "./infra-scripts/run-react.sh"
tmux attach -t "$session_name"