"""Module test_lib contains helper functions for tests."""

from typing import Any


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
