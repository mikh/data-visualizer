"""Module test_dir_tree_lib contains tests for the dir_tree_lib module."""

from typing import Dict, Any, List

import os
import json
import shutil

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from db import db_interface
import dir_tree_lib

TESTDATA_DIR = os.path.join("flask", "tests", "testdata")
TEST_DB_JSON_PATH = os.path.join(TESTDATA_DIR, "baseline-db.json")
TEST_DATA_FILE_DIR = os.path.join("flask", "untracked", "tests", "data")

_BASE_STRUCTURE = {
    "tree": {
        "test-folder-1": {
            "type": "folder",
            "full-path": "test-folder-1",
            "children": {
                "test-file-1": {
                    "type": "file",
                    "full-path": "test-folder-1/test-file-1",
                    "tags": ["tag-1", "tag-2"],
                },
                "test-file-3": {
                    "type": "file",
                    "full-path": "test-folder-1/test-file-3",
                    "tags": [],
                },
            },
        },
        "test-file-2": {
            "type": "file",
            "full-path": "test-file-2",
            "tags": ["tag-1"],
        },
    },
    "tags": ["tag-1", "tag-2"],
}


def make_test_db(empty: bool = False) -> Engine:
    """Make a test database."""
    engine = db_interface.make_engine(":memory:")

    if not empty:
        with Session(engine) as session:
            with open(TEST_DB_JSON_PATH, "r", encoding="utf-8") as file:
                test_db_json = json.load(file)
            db_interface.mass_add_objects(session, test_db_json)
    return engine


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


def get_all_files(base_dir: str) -> List[str]:
    """Get the list of all files in dir structure."""
    all_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            all_files.append(os.path.join(root[len(base_dir) + 1 :], file))
    return all_files


def test_get_all_tags():
    """Test the get_all_tags function."""
    engine = make_test_db()
    assert dir_tree_lib.get_all_tags(engine) == ["tag-1", "tag-2"]


def test_list_tree():
    """Test the list_tree function."""
    engine = make_test_db()
    assert dir_tree_lib.list_tree(engine) == _BASE_STRUCTURE


@pytest.mark.parametrize(
    "request_json, want_response, want_structure, want_data_files",
    [
        (
            {},
            {"error": "Path cannot be empty."},
            _BASE_STRUCTURE,
            ["test-file-1.csv", "data-folder-1/test-file-2.json"],
        ),
        (
            {"path": "fake-path"},
            {"error": "File metadata not found for path fake-path."},
            _BASE_STRUCTURE,
            ["test-file-1.csv", "data-folder-1/test-file-2.json"],
        ),
        (
            {"path": "test-folder-1/test-file-3"},
            {"error": "Data file not found for path fake-file.json."},
            _BASE_STRUCTURE,
            ["test-file-1.csv", "data-folder-1/test-file-2.json"],
        ),
        (
            {"path": "test-folder-1/test-file-1"},
            {},
            {
                "tree": {
                    "test-folder-1": {
                        "type": "folder",
                        "full-path": "test-folder-1",
                        "children": {
                            "test-file-3": {
                                "type": "file",
                                "full-path": "test-folder-1/test-file-3",
                                "tags": [],
                            },
                        },
                    },
                    "test-file-2": {
                        "type": "file",
                        "full-path": "test-file-2",
                        "tags": ["tag-1"],
                    },
                },
                "tags": ["tag-1", "tag-2"],
            },
            ["data-folder-1/test-file-2.json"],
        ),
    ],
    ids=[
        "empty-path-gives-error",
        "bad-path-gives-error",
        "bad-data-file-path-gives-error",
        "delete-file-removes-file-and-metadata",
    ],
)
def test_delete(
    request_json: Dict[str, Any],
    want_response: Dict[str, str],
    want_structure: Dict[str, Any],
    want_data_files: List[str],
):
    """Test the delete function."""
    engine = make_test_db()
    create_test_data_files(
        os.path.join(TESTDATA_DIR, "baseline"),
        TEST_DATA_FILE_DIR,
    )
    response = dir_tree_lib.delete(
        engine, request_json, data_file_dir=TEST_DATA_FILE_DIR
    )
    assert response == want_response
    assert dir_tree_lib.list_tree(engine) == want_structure
    assert get_all_files(TEST_DATA_FILE_DIR) == want_data_files


if __name__ == "__main__":
    create_test_data_files(
        os.path.join("tests", "testdata", "baseline"),
        os.path.join("untracked", "tests", "data"),
    )
