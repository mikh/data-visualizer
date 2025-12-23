"""Module test_db_interface contains tests for the db_interface module."""

from typing import Any, Dict, List

import os
import json
import copy

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from db import db_interface

TEST_DB_JSON_PATH = os.environ.get(
    "TEST_DB_JSON_PATH", os.path.join("flask", "tests", "testdata", "baseline-db.json")
)
COMPLETE_EXPORT_DB_JSON_PATH = os.environ.get(
    "COMPLETE_EXPORT_DB_JSON_PATH",
    os.path.join("flask", "tests", "testdata", "complete-export-db.json"),
)


def load_test_db_data() -> Dict[str, Any]:
    """Load test database data."""
    with open(TEST_DB_JSON_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


TEST_DB_DATA = load_test_db_data()


def make_test_db(empty: bool = False) -> Engine:
    """Make a test database."""
    engine = db_interface.make_engine(":memory:")

    if not empty:
        with Session(engine) as session:
            db_interface.mass_add_objects(session, copy.deepcopy(TEST_DB_DATA))
    return engine


def dict_compare(a: Any, b: Any) -> bool:
    """Compare two dictionaries or lists."""
    assert isinstance(a, type(b)), f"Types do not match {type(a)} != {type(b)}"
    if isinstance(a, dict):
        assert sorted(a.keys()) == sorted(
            b.keys()
        ), f"Keys do not match: {sorted(a.keys())} != {sorted(b.keys())}"
        for key in a.keys():
            assert isinstance(
                a[key], type(b[key])
            ), f"Types do not match for key {key}: {type(a[key])} != {type(b[key])}"
            if isinstance(a[key], (dict, list)):
                dict_compare(a[key], b[key])
            else:
                assert (
                    a[key] == b[key]
                ), f"Values do not match for key {key}: {a[key]} != {b[key]}"
    elif isinstance(a, list):
        assert len(a) == len(b), f"Lengths do not match: {len(a)} != {len(b)}"
        for i, item in enumerate(a):
            if isinstance(item, (dict, list)):
                dict_compare(item, b[i])
            else:
                assert (
                    item == b[i]
                ), f"Values do not match for index {i}: {item} != {b[i]}"
    else:
        assert a == b, f"Values do not match: {a} != {b}"
    return True


@pytest.mark.parametrize(
    "model_name, want",
    [
        ("file_metadata", TEST_DB_DATA["file_metadata"]),
        ("tag", [{"name": "tag-1"}, {"name": "tag-2"}]),
        (
            "file_stats",
            [
                {
                    "path": "test-folder-1/test-file-1",
                    "num_columns": 2,
                    "num_rows": 2,
                    "column_stats": [
                        {
                            "column_name": "column-1",
                            "data_type": "string",
                            "num_rows": 2,
                            "num_unique_values": 2,
                            "num_null_values": 0,
                            "num_zeros_values": 0,
                            "std_dev": 0.0,
                            "mean": 0.0,
                            "median": 0.0,
                            "min_value": 0.0,
                            "max_value": 0.0,
                            "num_empty_values": 0,
                        },
                        {
                            "column_name": "column-2",
                            "data_type": "string",
                            "num_rows": 2,
                            "num_unique_values": 2,
                            "num_null_values": 0,
                            "num_zeros_values": 0,
                            "std_dev": 0.0,
                            "mean": 0.0,
                            "median": 0.0,
                            "min_value": 0.0,
                            "max_value": 0.0,
                            "num_empty_values": 0,
                        },
                    ],
                },
                {
                    "path": "test-folder-3/test-sub-folder-1/test-file-5",
                    "num_columns": 2,
                    "num_rows": 2,
                    "column_stats": [
                        {
                            "column_name": "column-1",
                            "data_type": "string",
                            "num_rows": 2,
                            "num_unique_values": 2,
                            "num_null_values": 0,
                            "num_zeros_values": 0,
                            "std_dev": 0.0,
                            "mean": 0.0,
                            "median": 0.0,
                            "min_value": 0.0,
                            "max_value": 0.0,
                            "num_empty_values": 0,
                        },
                        {
                            "column_name": "column-2",
                            "data_type": "string",
                            "num_rows": 2,
                            "num_unique_values": 2,
                            "num_null_values": 0,
                            "num_zeros_values": 0,
                            "std_dev": 0.0,
                            "mean": 0.0,
                            "median": 0.0,
                            "min_value": 0.0,
                            "max_value": 0.0,
                            "num_empty_values": 0,
                        },
                    ],
                },
            ],
        ),
        (
            "column_stats",
            [
                {
                    "column_name": "column-1",
                    "data_type": "string",
                    "num_rows": 2,
                    "num_unique_values": 2,
                    "num_null_values": 0,
                    "num_zeros_values": 0,
                    "std_dev": 0.0,
                    "mean": 0.0,
                    "median": 0.0,
                    "min_value": 0.0,
                    "max_value": 0.0,
                    "num_empty_values": 0,
                },
                {
                    "column_name": "column-2",
                    "data_type": "string",
                    "num_rows": 2,
                    "num_unique_values": 2,
                    "num_null_values": 0,
                    "num_zeros_values": 0,
                    "std_dev": 0.0,
                    "mean": 0.0,
                    "median": 0.0,
                    "min_value": 0.0,
                    "max_value": 0.0,
                    "num_empty_values": 0,
                },
                {
                    "column_name": "column-1",
                    "data_type": "string",
                    "num_rows": 2,
                    "num_unique_values": 2,
                    "num_null_values": 0,
                    "num_zeros_values": 0,
                    "std_dev": 0.0,
                    "mean": 0.0,
                    "median": 0.0,
                    "min_value": 0.0,
                    "max_value": 0.0,
                    "num_empty_values": 0,
                },
                {
                    "column_name": "column-2",
                    "data_type": "string",
                    "num_rows": 2,
                    "num_unique_values": 2,
                    "num_null_values": 0,
                    "num_zeros_values": 0,
                    "std_dev": 0.0,
                    "mean": 0.0,
                    "median": 0.0,
                    "min_value": 0.0,
                    "max_value": 0.0,
                    "num_empty_values": 0,
                },
            ],
        ),
    ],
)
def test_get_all_of_model(model_name: str, want: List[Dict[str, Any]]):
    """Test get_all_of_model function."""
    engine = make_test_db()
    output_objects = db_interface.get_all_of_model(engine, model_name)
    dict_compare(output_objects, want)


@pytest.mark.parametrize(
    "model_name, key, value, want_dict",
    [
        (
            "file_metadata",
            "path",
            "test-folder-1/test-file-1",
            {
                "name": "test-file-1",
                "path": "test-folder-1/test-file-1",
                "data_file_type": "csv",
                "data_file_path": "test-file-1.csv",
                "tags": ["tag-1", "tag-2"],
                "file_stats": {
                    "path": "test-folder-1/test-file-1",
                    "num_columns": 2,
                    "num_rows": 2,
                    "column_stats": [
                        {
                            "column_name": "column-1",
                            "data_type": "string",
                            "num_rows": 2,
                            "num_unique_values": 2,
                            "num_null_values": 0,
                            "num_zeros_values": 0,
                            "std_dev": 0.0,
                            "mean": 0.0,
                            "median": 0.0,
                            "min_value": 0.0,
                            "max_value": 0.0,
                            "num_empty_values": 0,
                        },
                        {
                            "column_name": "column-2",
                            "data_type": "string",
                            "num_rows": 2,
                            "num_unique_values": 2,
                            "num_null_values": 0,
                            "num_zeros_values": 0,
                            "std_dev": 0.0,
                            "mean": 0.0,
                            "median": 0.0,
                            "min_value": 0.0,
                            "max_value": 0.0,
                            "num_empty_values": 0,
                        },
                    ],
                },
            },
        ),
        ("tag", "name", "tag-1", {"name": "tag-1"}),
        (
            "file_stats",
            "path",
            "test-folder-1/test-file-1",
            {
                "path": "test-folder-1/test-file-1",
                "num_columns": 2,
                "num_rows": 2,
                "column_stats": [
                    {
                        "column_name": "column-1",
                        "data_type": "string",
                        "num_rows": 2,
                        "num_unique_values": 2,
                        "num_null_values": 0,
                        "num_zeros_values": 0,
                        "std_dev": 0.0,
                        "mean": 0.0,
                        "median": 0.0,
                        "min_value": 0.0,
                        "max_value": 0.0,
                        "num_empty_values": 0,
                    },
                    {
                        "column_name": "column-2",
                        "data_type": "string",
                        "num_rows": 2,
                        "num_unique_values": 2,
                        "num_null_values": 0,
                        "num_zeros_values": 0,
                        "std_dev": 0.0,
                        "mean": 0.0,
                        "median": 0.0,
                        "min_value": 0.0,
                        "max_value": 0.0,
                        "num_empty_values": 0,
                    },
                ],
            },
        ),
        (
            "column_stats",
            "column_name",
            "column-1",
            {
                "column_name": "column-1",
                "data_type": "string",
                "num_rows": 2,
                "num_unique_values": 2,
                "num_null_values": 0,
                "num_zeros_values": 0,
                "std_dev": 0.0,
                "mean": 0.0,
                "median": 0.0,
                "min_value": 0.0,
                "max_value": 0.0,
                "num_empty_values": 0,
            },
        ),
        ("fake-model", "name", "value", None),
    ],
    ids=["file_metadata", "tag", "file_stats", "column_stats", "fake-model"],
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


NEW_COLUMN_STATS_1 = {
    "column_name": "column-new-1",
    "data_type": "string",
    "num_rows": 2,
    "num_unique_values": 2,
    "num_null_values": 0,
    "num_zeros_values": 0,
    "std_dev": 0.0,
    "mean": 0.0,
    "median": 0.0,
    "min_value": 0.0,
    "max_value": 0.0,
    "num_empty_values": 1,
}

NEW_COLUMN_STATS_2 = {
    "column_name": "column-new-2",
    "data_type": "integer",
    "num_rows": 2,
    "num_unique_values": 2,
    "num_null_values": 1,
    "num_zeros_values": 1,
    "std_dev": 3.0,
    "mean": 4.0,
    "median": 5.0,
    "min_value": 6.0,
    "max_value": 7.0,
    "num_empty_values": 0,
}

NEW_FILE_STATS = {
    "path": "test-file-new",
    "num_columns": 2,
    "num_rows": 2,
    "column_stats": [NEW_COLUMN_STATS_1, NEW_COLUMN_STATS_2],
}

NEW_FILE_METADATA = {
    "name": "test-file-new",
    "path": "test-file-new",
    "data_file_type": "csv",
    "data_file_path": "new-file.csv",
    "tags": ["tag-new", "tag-new-2"],
    "file_stats": NEW_FILE_STATS,
}


@pytest.mark.parametrize(
    "model_name, data, want",
    [
        ("fake-model", {"name": "value"}, None),
        (
            "file_metadata",
            {
                "name": "test-file-new",
                "path": "test-file-2",
                "data_file_type": "csv",
                "data_file_path": "some-new-path/new-file.csv",
                "tags": ["tag-new"],
                "file_stats": None,
            },
            {
                "name": "test-file-2",
                "path": "test-file-2",
                "data_file_type": "json",
                "data_file_path": "data-folder-1/test-file-2.json",
                "tags": ["tag-1"],
                "file_stats": None,
            },
        ),
        ("column_stats", NEW_COLUMN_STATS_1, NEW_COLUMN_STATS_1),
        ("file_stats", NEW_FILE_STATS, NEW_FILE_STATS),
        ("tag", {"name": "tag-new"}, {"name": "tag-new"}),
        ("file_metadata", NEW_FILE_METADATA, NEW_FILE_METADATA),
    ],
    ids=[
        "fake-model",
        "existing-object-returns-object",
        "new-column-stats",
        "new-file-stats",
        "new-tag",
        "new-file-metadata",
    ],
)
def test_create_or_get_object(
    model_name: str, data: Dict[str, Any], want: Dict[str, Any]
):
    """Test the create_or_get_object function."""
    data = copy.deepcopy(data)

    engine = make_test_db()
    with Session(engine) as session:
        output_db_object = db_interface.create_or_get_object(session, model_name, data)
        session.commit()
        if output_db_object is not None:
            output_db_object = output_db_object.to_dict()
        assert dict_compare(output_db_object, want)


def test_mass_add_objects():
    """Tests the mass_add_objects function."""
    engine = make_test_db(empty=True)
    assert db_interface.get_object_counts(engine) == {
        "file_metadata": 0,
        "tag": 0,
        "file_tags": 0,
        "file_stats": 0,
        "column_stats": 0,
    }

    with open(TEST_DB_JSON_PATH, "r", encoding="utf-8") as file:
        test_db_json = json.load(file)

    with Session(engine) as session:
        db_interface.mass_add_objects(session, test_db_json)
        session.commit()

    assert db_interface.get_object_counts(engine) == {
        "file_metadata": 5,
        "tag": 2,
        "file_tags": 3,
        "file_stats": 2,
        "column_stats": 4,
    }


def test_get_object_counts():
    """Tests the get_object_counts function."""
    engine = make_test_db()
    assert db_interface.get_object_counts(engine) == {
        "file_metadata": 5,
        "tag": 2,
        "file_tags": 3,
        "file_stats": 2,
        "column_stats": 4,
    }


@pytest.mark.parametrize(
    "export_all, want_path",
    [
        (False, TEST_DB_JSON_PATH),
        (True, COMPLETE_EXPORT_DB_JSON_PATH),
    ],
    ids=["export-all-false", "export-all-true"],
)
def test_export_db_objects(export_all: bool, want_path: str):
    """Tests the export_db_objects function."""
    engine = make_test_db()
    output_db_objects = db_interface.export_db_objects(engine, export_all=export_all)
    with open(want_path, "r", encoding="utf-8") as file:
        want_db_objects = json.load(file)
    assert dict_compare(output_db_objects, want_db_objects)
