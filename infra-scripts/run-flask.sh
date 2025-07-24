#!/bin/bash

. .venv/bin/activate

cd flask

export FILE_BASE_DIR="untracked/data"
export LOG_DIR="untracked/logs"

mkdir -p $FILE_BASE_DIR
mkdir -p $LOG_DIR

python run.py

sleep 99d