"""Module dir_tree_lib contains functions to view and modify the folder tree."""

from typing import List, Any, Dict, Union

import os
import json
import shutil

import logging_helper

VERBOSE = os.environ.get("VERBOSE_LOGGING", "false").lower() == "true"
LOG_DIRECTORY = os.environ.get("LOG_DIR", "logs")

logger = logging_helper.init_logging(
    __name__, VERBOSE, LOG_DIRECTORY, "dir_tree_lib.log"
)


def get_tags(full_path: str) -> Union[List[str]]:
    """Gets tags from a file."""
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        return []
    tags = data.get("tags", [])
    if isinstance(tags, str):
        tags = [x.strip() for x in tags.split(",")]
    return tags


def list_tree(
    tree_root: str,
) -> Dict[str, Union[Dict[str, Any], List[str]]]:
    """List all files and folders in the tree."""
    logger.debug("control=%s", "list")
    tree = {}
    all_tags = set()

    def _get_folder(path: List[str]):
        """Gets a folder from tree."""
        cur_folder = tree
        for folder in path:
            cur_folder = cur_folder[folder]["children"]
        return cur_folder

    for root, dirs, files in os.walk(tree_root):
        pruned_root = root[len(tree_root) + 1 :]
        pruned_root = [x.strip() for x in pruned_root.split("/") if x.strip()]

        target_folder = _get_folder(pruned_root)
        for directory in dirs:
            full_path = os.path.join(root, directory)
            target_folder[directory] = {
                "type": "folder",
                "full-path": full_path,
                "children": {},
            }
        for file in files:
            full_path = os.path.join(root, file)
            tags = [x.strip() for x in get_tags(full_path) if x.strip()]
            all_tags.update(tags)
            target_folder[file] = {
                "type": "file",
                "full-path": full_path,
                "tags": tags,
            }
    return {"tree": tree, "tags": sorted(list(all_tags))}


def delete(request_json: Dict[str, Any], tree_root: str) -> Dict[str, str]:
    """Delete a directory or file."""
    name = request_json.get("name", "")
    full_path = os.path.join(tree_root, name)
    delete_type = ""
    if os.path.isdir(full_path):
        delete_type = "dir"
    elif os.path.isfile(full_path):
        delete_type = "file"
    else:
        logger.error("Path %s does not exist.", full_path)
        return {"error": f"Path {full_path} does not exist."}
    logger.debug(
        "control=%s, delete_type=%s, name=%s, full_path=%s",
        "delete",
        delete_type,
        name,
        full_path,
    )
    if delete_type == "dir":
        shutil.rmtree(full_path)
    else:
        os.remove(full_path)
    return {}


def move(request_json: Dict[str, Any], tree_root: str) -> Dict[str, str]:
    """Moves a directory or file."""
    source = request_json.get("source", "")
    source_full = os.path.join(tree_root, source)
    if not os.path.exists(source_full):
        logger.error("Path %s does not exist.", source_full)
        return {"error": f"Path {source_full} does not exist."}

    dest = request_json.get("dest", "")
    if not dest:
        logger.error("Dest path cannot be empty.")
        return {"error": "Dest path cannot be empty."}
    dest_full = os.path.join(tree_root, dest)
    if os.path.exists(dest_full):
        logger.error("Dest path %s already exists", dest_full)
        return {"error": f"Dest path {dest_full} already exists."}

    logger.debug(
        "control=%s, source=%s, source_full=%s, dest=%s, dest_full=%s",
        "move",
        source,
        source_full,
        dest,
        dest_full,
    )
    shutil.move(source_full, dest_full)
    return {}


def load(request_json: Dict[str, Any], tree_root: str) -> Dict[str, Union[str, Any]]:
    """Loads a data file."""
    source = request_json.get("source", "")
    source_full = os.path.join(tree_root, source)
    if not os.path.exists(source_full):
        logger.error("Path %s does not exist.", source_full)
        return {"error": f"Path {source_full} does not exist."}

    logger.debug("control=%s, source=%s, source_full=%s", "load", source, source_full)
    with open(source_full, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["source_file"] = source
    logger.debug("%s", json.dumps(data))
    return {"data": data}


def copy(request_json: Dict[str, Any], tree_root: str) -> Dict[str, str]:
    """Copies a directory or file."""
    source = request_json.get("source", "")
    source_full = os.path.join(tree_root, source)
    if not os.path.exists(source_full):
        logger.error("Path %s does not exist.", source_full)
        return {"error": f"Path {source_full} does not exist."}
    dest = request_json.get("dest", "")
    if not dest:
        logger.error("Dest path cannot be empty.")
        return {"error": "Dest path cannot be empty."}
    dest_full = os.path.join(tree_root, dest)
    if os.path.exists(dest_full):
        logger.error("Dest path %s already exists", dest_full)
        return {"error": f"Dest path {dest_full} already exists"}
    if os.path.isdir(source_full):
        shutil.copytree(source_full, dest_full)
    else:
        shutil.copy2(source_full, dest_full)
    return {}


def upload(
    request_files: Dict[str, Any], request_json: Dict[str, Any], tree_root: str
) -> Dict[str, str]:
    """Uploads a file to the server."""
    print(request_files)
    print(request_json)
    return {}
