"""Module dir_tree_lib contains functions to view and modify the folder tree."""

from typing import List, Any, Dict, Union

import os
import json
import shutil

from sqlalchemy import Engine
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename

import logging_helper
from db import db_interface

VERBOSE = os.environ.get("VERBOSE_LOGGING", "false").lower() == "true"
LOG_DIRECTORY = os.environ.get("LOG_DIR", "logs")
DB_PATH = os.environ.get("DB_PATH", os.path.join("untracked", "metadata.sqlite"))

SUPPORTED_FILE_TYPES = ["csv", "json"]

# TODO: Move to using a database for metadata storage.
# TODO: On upload check for supported file types.
# TODO: On upload perform data-formats specific uploads
# TODO: Change delete/move/copy/etc to use the database instead of the file system

logger = logging_helper.init_logging(
    __name__, VERBOSE, LOG_DIRECTORY, "dir_tree_lib.log"
)


def get_all_tags(engine: Engine) -> Union[List[str]]:
    """Gets all tags from the database."""
    return db_interface.get_tag_list(engine)


def list_tree(
    engine: Engine,
) -> Dict[str, Union[Dict[str, Any], List[str]]]:
    """List all files and folders in the tree."""
    logger.debug("control=%s", "list")

    files = db_interface.get_file_list(engine)
    tags = db_interface.get_tag_list(engine)

    structure = {}
    for file in files:
        path = file["path"].split("/")
        cur_folder = structure
        cur_path = ""
        for folder in path[:-1]:
            if cur_path:
                cur_path = os.path.join(cur_path, folder)
            else:
                cur_path = folder
            if not folder in cur_folder:
                cur_folder[folder] = {
                    "type": "folder",
                    "full-path": cur_path,
                    "children": {},
                }
            cur_folder = cur_folder[folder]["children"]
        cur_folder[path[-1]] = {
            "type": "file",
            "full-path": file["path"],
            "tags": file["tags"],
        }

    return {"tree": structure, "tags": tags}


def delete(engine: Engine, request_json: Dict[str, Any]) -> Dict[str, str]:
    """Delete a file."""
    path = request_json.get("path", "")
    if not path:
        logger.error("Path cannot be empty.")
        return {"error": "Path cannot be empty."}
    logger.debug("control=%s, path=%s", "delete", path)
    with Session(engine) as session:
        file_metadata = db_interface.get_db_object_by_key(
            session, "file_metadata", "path", path
        )
        data_file_path = file_metadata.data_file_path
        # TODO: Delete the data file as well
    if file_metadata is None:
        logger.error("File metadata not found for path %s.", path)
        return {"error": f"File metadata not found for path {path}."}
    session.delete(file_metadata)
    session.commit()
    return {}


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
    request_files: Dict[str, Any], request_form: Dict[str, Any], tree_root: str
) -> Dict[str, str]:
    """Uploads a file to the server."""
    if not "file" in request_files:
        logger.error("File not found in request.")
        return {"error": "File not found in request."}
    if not "path" in request_form:
        logger.error("Path not found in request.")
        return {"error": "Path not found in request."}
    file = request_files["file"]
    if not file.filename:
        logger.error("File has no filename.")
        return {"error": "File has no filename."}
    extension = os.path.splitext(file.filename)[1].replace(".", "").lower()
    if extension not in SUPPORTED_FILE_TYPES:
        logger.error("File type %s not supported.", extension)
        return {"error": f"File type {extension} not supported."}
    path = request_form["path"]

    filename = secure_filename(file.filename)
    full_path = os.path.join(tree_root, path)
    file.save(full_path)
    logger.info("Saved file %s to %s", filename, full_path)

    return {}
