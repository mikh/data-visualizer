"""Module data_interface contains functions to interface with data files."""

from typing import Any, Tuple

import os
import json

import csv


def load_data_file(
    path: str, data_file_type: str, data_file_dir: str
) -> Tuple[Any, str]:
    """Loads a data file."""
    full_path = os.path.join(data_file_dir, path)
    if not os.path.exists(full_path):
        return None, f"Data file not found for path {path}."
    match data_file_type:
        case "json":
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data, ""
        case "csv":
            with open(full_path, "r", encoding="utf-8") as f:
                data = list(csv.reader(f))
            return data, ""
        case _:
            return None, f"Unsupported data file type: {data_file_type}."


def new_data_file_path(data_file_type: str, data_file_dir: str) -> str:
    """Creates a new data file path."""
    files = os.listdir(data_file_dir)
    files = [
        x.replace(f".{data_file_type}", "") for x in files if x.endswith(data_file_type)
    ]
    last_filename = 0
    for file in files:
        try:
            cur_filename = int(file)
            if cur_filename >= last_filename:
                last_filename = cur_filename + 1
        except ValueError:
            continue
    return f"{last_filename}.{data_file_type}"
