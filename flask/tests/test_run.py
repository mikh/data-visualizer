"""Module test_run contains tests for the run module."""

from typing import Dict, Any

import os

import pytest

import run
from tests import test_dir_tree_lib

VERSION_FILE = os.environ.get("VERSION_FILE", os.path.join("flask", "version"))


def test_version():
    """Tests version."""
    with open(VERSION_FILE, "r", encoding="utf-8") as file:
        want = file.read()
    got_response = run.app.test_client().get("/api/version")
    assert got_response.status_code == 200
    assert got_response.json["version"] == want


pytest.mark.parametrize("request_json, want_response", [], ids=[])


def test_tree_control(request_json: Dict[str, Any], want_response: Dict[str, Any]):
    """Test the tree control function."""
    # TODO: Build out test cases

    response = run.app.test_client().post("/api/tree", json=request_json)
    assert response.status_code == 200
    assert response.json == want_response
