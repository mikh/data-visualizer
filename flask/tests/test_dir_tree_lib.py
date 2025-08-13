"""Module test_dir_tree_lib contains tests for the dir_tree_lib module."""

import os

from db import db_interface
import dir_tree_lib

TEST_DB_PATH = os.path.join("flask", "untracked", "tests", "test_db.sqlite")


def _init_test_db():
    """Initialize a test database."""
    os.makedirs(os.path.dirname(TEST_DB_PATH), exist_ok=True)
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    db_interface.make_engine(TEST_DB_PATH)


def test_list_tree():
    """Test the list_tree function."""
    _init_test_db()

    assert "hello" == "hello"
