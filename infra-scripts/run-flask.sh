#!/bin/bash

. .venv/bin/activate

cd flask

export FILE_BASE_DIR="data"
python run.py

sleep 99d