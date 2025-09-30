"""Module test_db_interface contains tests for the db_interface module."""

from typing import Any, Dict

import os
import json

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from db import db_interface

TEST_DB_JSON_PATH = os.environ.get(
    "TEST_DB_JSON_PATH", os.path.join("flask", "tests", "testdata", "baseline-db.json")
)


def make_test_db(empty: bool = False) -> Engine:
    """Make a test database."""
    engine = db_interface.make_engine(":memory:")

    if not empty:
        with Session(engine) as session:
            with open(TEST_DB_JSON_PATH, "r", encoding="utf-8") as file:
                test_db_json = json.load(file)
            db_interface.mass_add_objects(session, test_db_json)
    return engine


def test_get_tag_list():
    """Test the get_tag_list function."""
    engine = make_test_db()
    tag_list = db_interface.get_tag_list(engine)
    assert tag_list == ["tag-1", "tag-2"]


def test_get_file_list():
    """Test the get_file_list function."""
    engine = make_test_db()
    file_list = db_interface.get_file_list(engine)
    assert file_list == [
        {
            "id": 1,
            "name": "test-file-1",
            "path": "test-folder-1/test-file-1",
            "data_file_type": "csv",
            "data_file_path": "test-file-1.csv",
            "tags": ["tag-1", "tag-2"],
        },
        {
            "id": 2,
            "name": "test-file-2",
            "path": "test-file-2",
            "data_file_type": "json",
            "data_file_path": "data-folder-1/test-file-2.json",
            "tags": ["tag-1"],
        },
        {
            "id": 3,
            "name": "test-file-3",
            "path": "test-folder-1/test-file-3",
            "data_file_type": "json",
            "data_file_path": "fake-file.json",
            "tags": [],
        },
        {
            "id": 4,
            "name": "test-file-4",
            "path": "test-folder-2/test-file-4",
            "data_file_type": "fake-data-type",
            "data_file_path": "test-file-1.csv",
            "tags": [],
        },
    ]


@pytest.mark.parametrize(
    "file_metadata, want, want_counts",
    [
        (
            {
                "name": "test-file-3",
                "path": "test-folder-1/test-file-1",
                "data_file_type": "json",
                "data_file_path": "some/path/to/test-file-3.json",
                "tags": ["tag-3"],
            },
            {
                "id": 1,
                "name": "test-file-1",
                "path": "test-folder-1/test-file-1",
                "data_file_type": "csv",
                "data_file_path": "test-file-1.csv",
                "tags": ["tag-1", "tag-2"],
            },
            {
                "file_metadata": 4,
                "tag": 2,
                "file_tags": 3,
            },
        ),
        (
            {
                "name": "test-file-5",
                "path": "test-folder-2/test-file-5",
                "data_file_type": "json",
                "data_file_path": "some/path/to/test-file-3.json",
                "tags": ["tag-3"],
            },
            {
                "id": 5,
                "name": "test-file-5",
                "path": "test-folder-2/test-file-5",
                "data_file_type": "json",
                "data_file_path": "some/path/to/test-file-3.json",
                "tags": ["tag-3"],
            },
            {"file_metadata": 5, "tag": 3, "file_tags": 4},
        ),
    ],
    ids=["existing-file", "new-file"],
)
def test_create_or_get_file_metadata(
    file_metadata: Dict[str, Any], want: Dict[str, Any], want_counts: Dict[str, int]
):
    """Tests the create_or_get_file_metadata function."""
    engine = make_test_db()
    with Session(engine) as session:
        output_db_object = db_interface.create_or_get_file_metadata(
            session, file_metadata
        )
        session.commit()
        assert output_db_object.to_dict() == want

    assert db_interface.get_object_counts(engine) == want_counts


@pytest.mark.parametrize(
    "tag, want, want_counts",
    [
        (
            "tag-1",
            {"id": 1, "name": "tag-1"},
            {"file_metadata": 4, "tag": 2, "file_tags": 3},
        ),
        (
            "tag-4",
            {"id": 3, "name": "tag-4"},
            {"file_metadata": 4, "tag": 3, "file_tags": 3},
        ),
    ],
    ids=["existing-tag", "new-tag"],
)
def test_create_or_get_tag(tag: str, want: Dict[str, Any], want_counts: Dict[str, int]):
    """Tests the create_or_get_tag function."""
    engine = make_test_db()
    with Session(engine) as session:
        output_db_object = db_interface.create_or_get_tag(session, tag)
        session.commit()
        assert output_db_object.to_dict() == want

    assert db_interface.get_object_counts(engine) == want_counts


def test_mass_add_objects():
    """Tests the mass_add_objects function."""
    engine = make_test_db(empty=True)
    assert db_interface.get_object_counts(engine) == {
        "file_metadata": 0,
        "tag": 0,
        "file_tags": 0,
    }

    with open(TEST_DB_JSON_PATH, "r", encoding="utf-8") as file:
        test_db_json = json.load(file)

    with Session(engine) as session:
        db_interface.mass_add_objects(session, test_db_json)
        session.commit()

    assert db_interface.get_object_counts(engine) == {
        "file_metadata": 4,
        "tag": 2,
        "file_tags": 3,
    }


def test_get_object_counts():
    """Tests the get_object_counts function."""
    engine = make_test_db()
    assert db_interface.get_object_counts(engine) == {
        "file_metadata": 4,
        "tag": 2,
        "file_tags": 3,
    }


@pytest.mark.parametrize(
    "model_name, key, value, want_dict",
    [
        (
            "file_metadata",
            "path",
            "test-folder-1/test-file-1",
            {
                "id": 1,
                "name": "test-file-1",
                "path": "test-folder-1/test-file-1",
                "data_file_type": "csv",
                "data_file_path": "test-file-1.csv",
                "tags": ["tag-1", "tag-2"],
            },
        ),
        ("tag", "name", "tag-1", {"id": 1, "name": "tag-1"}),
        ("fake-model", "name", "value", None),
    ],
    ids=["file_metadata", "tag", "fake-model"],
)
def test_get_db_object_by_key(
    model_name: str, key: str, value: Any, want_dict: Dict[str, Any]
):
    """Test get_db_object_by_key function."""
    engine = make_test_db()
    with Session(engine) as session:
        output_db_object = db_interface.get_db_object_by_key(
            session, model_name, key, value
        )
        if output_db_object is not None:
            output_db_object = output_db_object.to_dict()
        assert output_db_object == want_dict
