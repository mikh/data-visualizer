"""Module test_csv_analyzer tests the csv_analyzer module."""

import os

from data import csv_analyzer
from tests.test_lib import dict_compare

TESTDATA_DIR = os.environ.get(
    "TESTDATA_DIR", os.path.join("flask", "tests", "testdata")
)


def test_analyze_csv_stats():
    """Test the analyze_csv_stats function."""
    file_path = os.path.join(TESTDATA_DIR, "test-csv.csv")
    stats = csv_analyzer.analyze_csv_stats(file_path)

    want_stats = {
        "num_columns": 3,
        "num_rows": 4,
        "column_stats": [
            {
                "column_name": "column-1",
                "data_type": "numeric",
                "num_rows": 4,
                "num_unique_values": 4,
                "num_null_values": 0,
                "num_zeros_values": 1,
                "std_dev": 1.707825127659933,
                "mean": 1.75,
                "median": 1.5,
                "min_value": 0.0,
                "max_value": 4.0,
            },
            {
                "column_name": "column-2",
                "data_type": "string",
                "num_rows": 4,
                "num_unique_values": 3,
                "num_null_values": 1,
                "num_empty_values": 0,
            },
            {
                "column_name": "column-3",
                "data_type": "numeric",
                "num_rows": 4,
                "num_unique_values": 2,
                "num_null_values": 1,
                "num_zeros_values": 0,
                "std_dev": 0.5773502691896258,
                "mean": 3.3333333333333335,
                "median": 3.0,
                "min_value": 3.0,
                "max_value": 4.0,
            },
        ],
    }
    dict_compare(stats, want_stats)
