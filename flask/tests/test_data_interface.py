"""Module test_data_interface contains tests for the data_interface module."""

from typing import Any, Union

import os
import shutil

import pytest

from db import data_interface


TESTDATA_DIR = os.path.join("flask", "tests", "testdata")
TEST_DATA_FILE_DIR = os.path.join("flask", "untracked", "tests", "data")


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
def test_load_data_file(
    path: str, data_file_type: str, want_data: Any, want_error: Union[str, None]
):
    """Test the load_data_file function."""
    create_test_data_files(
        os.path.join(TESTDATA_DIR, "baseline"),
        TEST_DATA_FILE_DIR,
    )
    data, error = data_interface.load_data_file(
        path, data_file_type, TEST_DATA_FILE_DIR
    )
    assert data == want_data
    assert error == want_error
