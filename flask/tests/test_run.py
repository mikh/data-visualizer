"""Module test_run contains tests for the run module."""

from typing import Dict, Any

import os
import json
import shutil
import io

import pytest
from werkzeug.datastructures import FileStorage

import run
import dir_tree_lib
from db import db_interface
from tests import test_dir_tree_lib

VERSION_FILE = os.environ.get("VERSION_FILE", os.path.join("flask", "version"))

# Test configuration
TESTDATA_DIR = os.environ.get(
    "TESTDATA_DIR", os.path.join("flask", "tests", "testdata")
)
TEST_DB_JSON_PATH = os.environ.get(
    "TEST_DB_JSON_PATH", os.path.join(TESTDATA_DIR, "baseline-db.json")
)
TEST_DATA_FILE_DIR = os.environ.get(
    "TEST_DATA_FILE_DIR", os.path.join("flask", "untracked", "tests", "data")
)


def setup_test_environment():
    """Set up test database and data files."""
    # Create test database in untracked/tests directory
    test_db_dir = os.path.join("flask", "untracked", "tests")
    os.makedirs(test_db_dir, exist_ok=True)
    test_db_path = os.path.join(test_db_dir, "test_metadata.sqlite")

    # Create test data files
    test_dir_tree_lib.create_test_data_files(
        os.path.join(TESTDATA_DIR, "baseline"),
        TEST_DATA_FILE_DIR,
    )

    # Create test database
    engine = db_interface.make_engine(test_db_path)
    with db_interface.Session(engine) as session:
        with open(TEST_DB_JSON_PATH, "r", encoding="utf-8") as file:
            test_db_json = json.load(file)
        db_interface.mass_add_objects(session, test_db_json)

    return test_db_path


def test_version():
    """Tests version."""
    with open(VERSION_FILE, "r", encoding="utf-8") as file:
        want = file.read()
    got_response = run.app.test_client().get("/api/version")
    assert got_response.status_code == 200
    assert got_response.json["version"] == want


@pytest.mark.parametrize(
    "request_json, want_response",
    [
        # Test list control
        (
            {"control": "list"},
            test_dir_tree_lib._BASE_STRUCTURE,  # pylint: disable=protected-access
        ),
        # Test delete control - successful case
        (
            {"control": "delete", "path": "test-folder-1/test-file-1"},
            {},
        ),
        # Test delete control - error case
        (
            {"control": "delete", "path": ""},
            {"error": "Path cannot be empty."},
        ),
        # Test move control - successful case
        (
            {
                "control": "move",
                "source": "test-folder-1/test-file-1",
                "dest": "test-folder-2/test-file-1",
            },
            {},
        ),
        # Test move control - error case
        (
            {"control": "move", "source": "", "dest": "test-folder-2/test-file-1"},
            {"error": "Source path cannot be empty."},
        ),
        # Test copy control - successful case
        (
            {
                "control": "copy",
                "source": "test-folder-1/test-file-1",
                "dest": "test-folder-2/test-file-copy",
            },
            {},
        ),
        # Test copy control - error case
        (
            {
                "control": "copy",
                "source": "fake-source",
                "dest": "test-folder-2/test-file-1",
            },
            {"error": "Source file metadata not found for path fake-source."},
        ),
        # Test load control - successful case
        (
            {"control": "load", "path": "test-folder-1/test-file-1"},
            {
                "id": 1,
                "name": "test-file-1",
                "path": "test-folder-1/test-file-1",
                "data_file_type": "csv",
                "data_file_path": "test-file-1.csv",
                "tags": ["tag-1", "tag-2"],
                "data": [
                    ["column-1", "column-2"],
                    ["value-1", "value-2"],
                    ["value-3", "value-4"],
                ],
            },
        ),
        # Test load control - error case
        (
            {"control": "load", "path": ""},
            {"error": "Path cannot be empty."},
        ),
        # Test update control - successful case
        (
            {
                "control": "update",
                "path": "test-folder-1/test-file-1",
                "name": "test-file-1-updated",
                "tags": ["tag-3"],
            },
            {},
        ),
        # Test update control - error case
        (
            {"control": "update", "path": ""},
            {"error": "Path cannot be empty."},
        ),
        # Test invalid control
        (
            {"control": "invalid"},
            {"error": "Invalid control: invalid"},
        ),
    ],
    ids=[
        "list-control",
        "delete-control-success",
        "delete-control-error",
        "move-control-success",
        "move-control-error",
        "copy-control-success",
        "copy-control-error",
        "load-control-success",
        "load-control-error",
        "update-control-success",
        "update-control-error",
        "invalid-control",
    ],
)
def test_tree_control(request_json: Dict[str, Any], want_response: Dict[str, Any]):
    """Test the tree control function."""
    # Set up test environment
    test_db_path = setup_test_environment()

    # Override the DB_PATH for testing
    original_db_path = dir_tree_lib.DB_PATH
    dir_tree_lib.DB_PATH = test_db_path
    original_data_file_dir = dir_tree_lib.DATA_FILE_DIR
    dir_tree_lib.DATA_FILE_DIR = TEST_DATA_FILE_DIR

    try:
        # Make the request
        response = run.app.test_client().post("/api/tree", json=request_json)

        # Assert response
        assert response.status_code == 200
        assert response.json == want_response

    finally:
        # Restore original DB_PATH
        dir_tree_lib.DB_PATH = original_db_path
        dir_tree_lib.DATA_FILE_DIR = original_data_file_dir

        # Clean up test files
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        if os.path.exists(TEST_DATA_FILE_DIR):
            shutil.rmtree(TEST_DATA_FILE_DIR)


def test_upload_file():
    """Test the upload file function - successful upload case."""
    # Set up test environment
    test_db_path = setup_test_environment()

    # Override the DB_PATH and DATA_FILE_DIR for testing
    original_db_path = dir_tree_lib.DB_PATH
    dir_tree_lib.DB_PATH = test_db_path
    original_data_file_dir = dir_tree_lib.DATA_FILE_DIR
    dir_tree_lib.DATA_FILE_DIR = TEST_DATA_FILE_DIR

    try:
        # Prepare the multipart form data for successful upload
        data = {
            "path": "test-folder-1/test-upload",
            "file": (
                FileStorage(
                    filename="test.csv", stream=io.BytesIO(b"col1,col2\nval1,val2")
                ),
                "test.csv",
            ),
        }

        # Make the POST request
        response = run.app.test_client().post("/api/upload", data=data)

        # Assert response
        assert response.status_code == 200
        assert response.json == {}

    finally:
        # Restore original paths
        dir_tree_lib.DB_PATH = original_db_path
        dir_tree_lib.DATA_FILE_DIR = original_data_file_dir

        # Clean up test files
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        if os.path.exists(TEST_DATA_FILE_DIR):
            shutil.rmtree(TEST_DATA_FILE_DIR)
