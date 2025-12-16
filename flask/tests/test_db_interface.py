"""Module test_db_interface contains tests for the db_interface module."""

from typing import Any, Dict, List, Union

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


def load_test_db_data() -> Dict[str, Any]:
    """Load test database data."""
    with open(TEST_DB_JSON_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


TEST_DB_DATA = load_test_db_data()

# TODO: Update tests for model/db_interface rework.


def make_test_db(empty: bool = False) -> Engine:
    """Make a test database."""
    engine = db_interface.make_engine(":memory:")

    if not empty:
        with Session(engine) as session:
            db_interface.mass_add_objects(session, copy.deepcopy(TEST_DB_DATA))
    return engine


def strip_id_from_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Strip the id from the data."""
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) or isinstance(item, list):
                item = strip_id_from_dict(item, keys)
    elif isinstance(data, dict):
        for key, value in data.items():
            if key in keys:
                continue
            if isinstance(value, dict) or isinstance(value, list):
                value = strip_id_from_dict(value, keys)
        data[key] = value
    return data


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
    # output_objects = [
    #     strip_id_from_dict(obj, ["id", "file_stats_id"]) for obj in output_objects
    # ]
    dict_compare(output_objects, want)


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
        {
            "id": 5,
            "name": "test-file-5",
            "path": "test-folder-3/test-sub-folder-1/test-file-5",
            "data_file_type": "csv",
            "data_file_path": "test-file-5.csv",
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
                "file_metadata": 5,
                "tag": 2,
                "file_tags": 3,
            },
        ),
        (
            {
                "name": "test-file-6",
                "path": "test-folder-2/test-file-6",
                "data_file_type": "json",
                "data_file_path": "some/path/to/test-file-3.json",
                "tags": ["tag-3"],
            },
            {
                "id": 6,
                "name": "test-file-6",
                "path": "test-folder-2/test-file-6",
                "data_file_type": "json",
                "data_file_path": "some/path/to/test-file-3.json",
                "tags": ["tag-3"],
            },
            {"file_metadata": 6, "tag": 3, "file_tags": 4},
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
            {"file_metadata": 5, "tag": 2, "file_tags": 3},
        ),
        (
            "tag-4",
            {"id": 3, "name": "tag-4"},
            {"file_metadata": 5, "tag": 3, "file_tags": 3},
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
        "file_metadata": 5,
        "tag": 2,
        "file_tags": 3,
    }


def test_get_object_counts():
    """Tests the get_object_counts function."""
    engine = make_test_db()
    assert db_interface.get_object_counts(engine) == {
        "file_metadata": 5,
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


def test_export_db_objects():
    """Tests the export_db_objects function."""
    engine = make_test_db()
    with Session(engine) as session:
        output_db_objects = db_interface.export_db_objects(session)
        with open(TEST_DB_JSON_PATH, "r", encoding="utf-8") as file:
            want_db_objects = json.load(file)
        assert output_db_objects == want_db_objects
