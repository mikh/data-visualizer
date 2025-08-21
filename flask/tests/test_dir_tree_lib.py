"""Module test_dir_tree_lib contains tests for the dir_tree_lib module."""

import os
import json

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from db import db_interface
import dir_tree_lib


TEST_DB_JSON_PATH = os.path.join("flask", "tests", "testdata", "baseline-db.json")


def make_test_db(empty: bool = False) -> Engine:
    """Make a test database."""
    engine = db_interface.make_engine(":memory:")

    if not empty:
        with Session(engine) as session:
            with open(TEST_DB_JSON_PATH, "r", encoding="utf-8") as file:
                test_db_json = json.load(file)
            db_interface.mass_add_objects(session, test_db_json)
    return engine


def test_get_all_tags():
    """Test the get_all_tags function."""
    engine = make_test_db()
    assert dir_tree_lib.get_all_tags(engine) == ["tag-1", "tag-2"]


def test_list_tree():
    """Test the list_tree function."""
    engine = make_test_db()
    assert dir_tree_lib.list_tree(engine) == {
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
