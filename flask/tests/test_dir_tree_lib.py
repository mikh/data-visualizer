"""Module test_dir_tree_lib contains tests for the dir_tree_lib module."""

from typing import Dict, Any, List

import os
import json
import shutil
import copy

import pytest
from werkzeug.datastructures import FileStorage
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
        "test-folder-2": {
            "type": "folder",
            "full-path": "test-folder-2",
            "children": {
                "test-file-4": {
                    "type": "file",
                    "full-path": "test-folder-2/test-file-4",
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
            sorted(
                ["0.csv", "test-file-1.csv", "3.json", "data-folder-1/test-file-2.json"]
            ),
        ),
        (
            {"path": "fake-path"},
            {"error": "File metadata not found for path fake-path."},
            _BASE_STRUCTURE,
            sorted(
                ["0.csv", "test-file-1.csv", "3.json", "data-folder-1/test-file-2.json"]
            ),
        ),
        (
            {"path": "test-folder-1/test-file-3"},
            {"error": "Data file not found for path fake-file.json."},
            _BASE_STRUCTURE,
            sorted(
                ["0.csv", "test-file-1.csv", "3.json", "data-folder-1/test-file-2.json"]
            ),
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
                    "test-folder-2": {
                        "type": "folder",
                        "full-path": "test-folder-2",
                        "children": {
                            "test-file-4": {
                                "type": "file",
                                "full-path": "test-folder-2/test-file-4",
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
            sorted(["0.csv", "3.json", "data-folder-1/test-file-2.json"]),
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
    response = dir_tree_lib.tree_delete(
        engine, request_json, data_file_dir=TEST_DATA_FILE_DIR
    )
    assert response == want_response
    assert dir_tree_lib.list_tree(engine) == want_structure
    assert sorted(get_all_files(TEST_DATA_FILE_DIR)) == want_data_files


@pytest.mark.parametrize(
    "request_json, want_response, want_structure",
    [
        ({}, {"error": "Source path cannot be empty."}, _BASE_STRUCTURE),
        (
            {"source": "fake-source"},
            {"error": "Dest path cannot be empty."},
            _BASE_STRUCTURE,
        ),
        (
            {"source": "fake-source", "dest": "test-folder-1/test-file-1"},
            {"error": "Source file metadata not found for path fake-source."},
            _BASE_STRUCTURE,
        ),
        (
            {
                "source": "test-folder-1/test-file-1",
                "dest": "test-folder-1/test-file-1",
            },
            {
                "error": "Dest file metadata already exists for path test-folder-1/test-file-1."
            },
            _BASE_STRUCTURE,
        ),
        (
            {
                "source": "test-folder-1/test-file-1",
                "dest": "test-folder-2/test-file-1",
            },
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
                    "test-folder-2": {
                        "type": "folder",
                        "full-path": "test-folder-2",
                        "children": {
                            "test-file-1": {
                                "type": "file",
                                "full-path": "test-folder-2/test-file-1",
                                "tags": ["tag-1", "tag-2"],
                            },
                            "test-file-4": {
                                "type": "file",
                                "full-path": "test-folder-2/test-file-4",
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
        ),
    ],
    ids=[
        "empty-source-gives-error",
        "empty-dest-gives-error",
        "bad-source-gives-error",
        "bad-dest-gives-error",
        "move-file",
    ],
)
def test_move(
    request_json: Dict[str, Any],
    want_response: Dict[str, str],
    want_structure: Dict[str, Any],
):
    """Test the move function."""
    engine = make_test_db()
    response = dir_tree_lib.move(engine, request_json)
    assert response == want_response
    assert dir_tree_lib.list_tree(engine) == want_structure


@pytest.mark.parametrize(
    "request_json, want_response, want_structure",
    [
        ({}, {"error": "Source path cannot be empty."}, _BASE_STRUCTURE),
        (
            {"source": "fake-source"},
            {"error": "Dest path cannot be empty."},
            _BASE_STRUCTURE,
        ),
        (
            {"source": "fake-source", "dest": "test-folder-1/test-file-1"},
            {"error": "Source file metadata not found for path fake-source."},
            _BASE_STRUCTURE,
        ),
        (
            {
                "source": "test-folder-1/test-file-1",
                "dest": "test-folder-1/test-file-1",
            },
            {
                "error": "Dest file metadata already exists for path test-folder-1/test-file-1."
            },
            _BASE_STRUCTURE,
        ),
        (
            {
                "source": "test-folder-1/test-file-1",
                "dest": "test-folder-2/test-file-1",
            },
            {},
            {
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
                    "test-folder-2": {
                        "type": "folder",
                        "full-path": "test-folder-2",
                        "children": {
                            "test-file-1": {
                                "type": "file",
                                "full-path": "test-folder-2/test-file-1",
                                "tags": ["tag-1", "tag-2"],
                            },
                            "test-file-4": {
                                "type": "file",
                                "full-path": "test-folder-2/test-file-4",
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
        ),
    ],
    ids=[
        "empty-source-gives-error",
        "empty-dest-gives-error",
        "bad-source-gives-error",
        "bad-dest-gives-error",
        "copy-file",
    ],
)
def test_copy(
    request_json: Dict[str, Any],
    want_response: Dict[str, str],
    want_structure: Dict[str, Any],
):
    """Test the move function."""
    engine = make_test_db()
    response = dir_tree_lib.copy(engine, request_json)
    assert response == want_response
    assert dir_tree_lib.list_tree(engine) == want_structure


@pytest.mark.parametrize(
    "request_json, want_response",
    [
        ({}, {"error": "Path cannot be empty."}),
        (
            {"path": "fake-path"},
            {"error": "File metadata not found for path fake-path."},
        ),
        (
            {"path": "test-folder-1/test-file-3"},
            {"error": "Data file not found for path fake-file.json."},
        ),
        (
            {"path": "test-folder-2/test-file-4"},
            {"error": "Unsupported data file type: fake-data-type."},
        ),
        (
            {"path": "test-folder-1/test-file-1"},
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
    ],
    ids=[
        "empty-path-gives-error",
        "bad-path-gives-error",
        "bad-data-file-path-gives-error",
        "bad-data-file-type-gives-error",
        "load-file",
    ],
)
def test_load(request_json: Dict[str, Any], want_response: Dict[str, Any]):
    """Test the load function."""
    engine = make_test_db()
    create_test_data_files(
        os.path.join(TESTDATA_DIR, "baseline"),
        TEST_DATA_FILE_DIR,
    )
    response = dir_tree_lib.load(engine, request_json, data_file_dir=TEST_DATA_FILE_DIR)
    assert response == want_response


@pytest.mark.parametrize(
    "request_files, request_form, want",
    [
        ({}, {}, {"error": "File not found in request."}),
        ({"file": FileStorage()}, {}, {"error": "File has no filename."}),
        (
            {"file": FileStorage(filename="test.pdf")},
            {},
            {"error": "File type pdf is not supported."},
        ),
        (
            {"file": FileStorage(filename="test.csv")},
            {},
            {"error": "Path not found in request."},
        ),
        (
            {"file": FileStorage(filename="test.csv")},
            {"path": "test-folder-1/test-file-1"},
            {"error": "Path test-folder-1/test-file-1 already exists."},
        ),
    ],
    ids=[
        "no-file-in-request-gives-error",
        "no-filename-in-file-gives-error",
        "unsupported-extension-gives-error",
        "no-path-gives-error",
        "existing-path-gives-error",
    ],
)
def test_upload_errors(
    request_files: Dict[str, Any], request_form: Dict[str, Any], want: Dict[str, str]
):
    """Test upload errors."""
    engine = make_test_db()
    create_test_data_files(os.path.join(TESTDATA_DIR, "baseline"), TEST_DATA_FILE_DIR)
    response = dir_tree_lib.upload(
        engine, request_files, request_form, data_file_dir=TEST_DATA_FILE_DIR
    )
    assert response == want


def test_upload_success():
    """Tests upload success."""
    engine = make_test_db()
    create_test_data_files(os.path.join(TESTDATA_DIR, "baseline"), TEST_DATA_FILE_DIR)

    assert dir_tree_lib.list_tree(engine) == _BASE_STRUCTURE
    assert sorted(get_all_files(TEST_DATA_FILE_DIR)) == sorted(
        [
            "0.csv",
            "test-file-1.csv",
            "3.json",
            "data-folder-1/test-file-2.json",
        ]
    )

    assert not dir_tree_lib.upload(
        engine,
        {"file": FileStorage(filename="test.csv")},
        {"path": "test-folder-1/test-5"},
        data_file_dir=TEST_DATA_FILE_DIR,
    )

    new_structure = copy.deepcopy(_BASE_STRUCTURE)
    new_structure["tree"]["test-folder-1"]["children"]["test-5"] = {
        "type": "file",
        "full-path": "test-folder-1/test-5",
        "tags": [],
    }
    assert dir_tree_lib.list_tree(engine) == new_structure
    assert sorted(get_all_files(TEST_DATA_FILE_DIR)) == sorted(
        [
            "0.csv",
            "1.csv",
            "test-file-1.csv",
            "3.json",
            "data-folder-1/test-file-2.json",
        ]
    )


_BASELINE_TEST_FILE_1 = {
    "id": 1,
    "name": "test-file-1",
    "path": "test-folder-1/test-file-1",
    "data_file_type": "csv",
    "data_file_path": "test-file-1.csv",
    "tags": ["tag-1", "tag-2"],
}


@pytest.mark.parametrize(
    "request_json, want_response, want_object_data",
    [
        ({}, {"error": "Path cannot be empty."}, _BASELINE_TEST_FILE_1),
        (
            {"path": "fake-path"},
            {"error": "File metadata not found for path fake-path."},
            _BASELINE_TEST_FILE_1,
        ),
        (
            {
                "path": "test-folder-1/test-file-1",
                "name": "test-file-1-new",
                "data_file_type": "json",
                "data_file_path": "test-file-1.json",
                "tags": ["tag-3"],
            },
            {},
            {
                **_BASELINE_TEST_FILE_1,
                "name": "test-file-1-new",
                "data_file_type": "json",
                "data_file_path": "test-file-1.json",
                "tags": ["tag-3"],
            },
        ),
    ],
    ids=[
        "empty-path-gives-error",
        "bad-path-gives-error",
        "update-file",
    ],
)
def test_update(
    request_json: Dict[str, Any],
    want_response: Dict[str, str],
    want_object_data: Dict[str, Any],
):
    """Tests the update function."""
    engine = make_test_db()
    response = dir_tree_lib.update(engine, request_json)
    assert response == want_response
    with Session(engine) as session:
        assert (
            db_interface.get_db_object_by_key(
                session, "file_metadata", "path", "test-folder-1/test-file-1"
            ).to_dict()
            == want_object_data
        )


if __name__ == "__main__":
    create_test_data_files(
        os.path.join("tests", "testdata", "baseline"),
        os.path.join("untracked", "tests", "data"),
    )
