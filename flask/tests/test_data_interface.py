"""Module test_data_interface contains tests for the data_interface module."""

import os
import shutil
from typing import Any

import pytest
from db import data_interface

TESTDATA_DIR = os.environ.get("TESTDATA_DIR", os.path.join("flask", "tests", "testdata"))
TEST_DATA_FILE_DIR = os.environ.get(
    "TEST_DATA_FILE_DIR", os.path.join("flask", "untracked", "tests", "data")
)


def create_test_data_files(testdata_files_dir: str, data_file_dir: str):
    """Create test data files."""
    if os.path.isdir(data_file_dir):
        shutil.rmtree(data_file_dir)
    os.makedirs(data_file_dir)
    for root, _, files in os.walk(testdata_files_dir):
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(data_file_dir, src[len(testdata_files_dir) + 1 :])
            dst_dir = os.path.dirname(dst)
            os.makedirs(dst_dir, exist_ok=True)
            shutil.copy(src, dst)


@pytest.mark.parametrize(
    "path, data_file_type, want_data, want_error",
    [
        ("fake-path", "json", None, "Data file not found for path fake-path."),
        (
            "test-file-1.csv",
            "fake-data-type",
            None,
            "Unsupported data file type: fake-data-type.",
        ),
        (
            "test-file-1.csv",
            "csv",
            [["column-1", "column-2"], ["value-1", "value-2"], ["value-3", "value-4"]],
            "",
        ),
        ("data-folder-1/test-file-2.json", "json", {"column-1": "value-1"}, ""),
    ],
    ids=[
        "fake-path",
        "fake-data-type",
        "csv",
        "json",
    ],
)
def test_load_data_file(path: str, data_file_type: str, want_data: Any, want_error: str | None):
    """Test the load_data_file function."""
    create_test_data_files(
        os.path.join(TESTDATA_DIR, "baseline"),
        TEST_DATA_FILE_DIR,
    )
    data, error = data_interface.load_data_file(path, data_file_type, TEST_DATA_FILE_DIR)
    assert data == want_data
    assert error == want_error


@pytest.mark.parametrize(
    "data_file_type, want",
    [("csv", "1.csv"), ("json", "4.json")],
    ids=["new-csv-filename", "new-json-filename"],
)
def test_new_data_file_path(data_file_type: str, want: str):
    """Test new_data_file_path function."""
    create_test_data_files(os.path.join(TESTDATA_DIR, "baseline"), TEST_DATA_FILE_DIR)
    assert data_interface.new_data_file_path(data_file_type, TEST_DATA_FILE_DIR) == want


@pytest.mark.parametrize(
    "data_file_type, path, want, expected_exception",
    [
        (
            "csv",
            os.path.join(TESTDATA_DIR, "test-csv.csv"),
            {
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
            },
            None,
        ),
        (
            "json",
            os.path.join(TESTDATA_DIR, "baseline", "3.json"),
            None,
            NotImplementedError,
        ),
        (
            "xml",
            os.path.join(TESTDATA_DIR, "test-csv.csv"),
            None,
            KeyError,
        ),
    ],
    ids=["test-csv", "test-json-failure", "test-unknown-type-failure"],
)
def test_analyze_data_file(
    data_file_type: str,
    path: str,
    want: dict[str, Any] | None,
    expected_exception: type[Exception] | None,
):
    """Tests analyze data."""
    if expected_exception is not None:
        with pytest.raises(expected_exception):
            data_interface.analyze_data_file(data_file_type, path)
    else:
        assert data_interface.analyze_data_file(data_file_type, path) == want
