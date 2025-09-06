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
from db import data_interface

VERBOSE = os.environ.get("VERBOSE_LOGGING", "false").lower() == "true"
LOG_DIRECTORY = os.environ.get("LOG_DIR", os.path.join("flask", "untracked", "logs"))
DB_PATH = os.environ.get("DB_PATH", os.path.join("untracked", "metadata.sqlite"))
DATA_FILE_DIR = os.environ.get("DATA_FILE_DIR", os.path.join("untracked", "data"))

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


def delete(
    engine: Engine,
    request_json: Dict[str, Any],
    data_file_dir: str = DATA_FILE_DIR,
) -> Dict[str, str]:
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

        if file_metadata is None:
            logger.error("File metadata not found for path %s.", path)
            return {"error": f"File metadata not found for path {path}."}

        data_file_path = file_metadata.data_file_path
        data_file_full_path = os.path.join(data_file_dir, data_file_path)
        if not os.path.exists(data_file_full_path):
            logger.error("Data file not found for path %s.", data_file_path)
            return {"error": f"Data file not found for path {data_file_path}."}
        os.remove(data_file_full_path)
        logger.info("Deleted data file %s.", data_file_full_path)

        session.delete(file_metadata)
        session.commit()
    return {}


def move(engine: Engine, request_json: Dict[str, Any]) -> Dict[str, str]:
    """Moves a file."""
    source = request_json.get("source", "")
    dest = request_json.get("dest", "")
    if not source:
        logger.error("Source path cannot be empty.")
        return {"error": "Source path cannot be empty."}
    if not dest:
        logger.error("Dest path cannot be empty.")
        return {"error": "Dest path cannot be empty."}
    logger.debug("control=%s, source=%s, dest=%s", "move", source, dest)
    with Session(engine) as session:
        source_file_metadata = db_interface.get_db_object_by_key(
            session, "file_metadata", "path", source
        )
        if source_file_metadata is None:
            logger.error("Source file metadata not found for path %s.", source)
            return {"error": f"Source file metadata not found for path {source}."}
        dest_file_metadata = db_interface.get_db_object_by_key(
            session, "file_metadata", "path", dest
        )
        if dest_file_metadata is not None:
            logger.error("Dest file metadata already exists for path %s.", dest)
            return {"error": f"Dest file metadata already exists for path {dest}."}
        source_file_metadata.path = dest
        session.commit()
    return {}


def copy(engine: Engine, request_json: Dict[str, Any]) -> Dict[str, str]:
    """Moves a file."""
    source = request_json.get("source", "")
    dest = request_json.get("dest", "")
    if not source:
        logger.error("Source path cannot be empty.")
        return {"error": "Source path cannot be empty."}
    if not dest:
        logger.error("Dest path cannot be empty.")
        return {"error": "Dest path cannot be empty."}
    logger.debug("control=%s, source=%s, dest=%s", "move", source, dest)
    with Session(engine) as session:
        source_file_metadata = db_interface.get_db_object_by_key(
            session, "file_metadata", "path", source
        )
        if source_file_metadata is None:
            logger.error("Source file metadata not found for path %s.", source)
            return {"error": f"Source file metadata not found for path {source}."}
        dest_file_metadata = db_interface.get_db_object_by_key(
            session, "file_metadata", "path", dest
        )
        if dest_file_metadata is not None:
            logger.error("Dest file metadata already exists for path %s.", dest)
            return {"error": f"Dest file metadata already exists for path {dest}."}
        db_interface.create_or_get_file_metadata(
            session,
            {
                "path": dest,
                "name": source_file_metadata.name,
                "data_file_type": source_file_metadata.data_file_type,
                "data_file_path": source_file_metadata.data_file_path,
                "tags": source_file_metadata.get_tags(),
            },
        )
        session.commit()
    return {}


def load(
    engine: Engine, request_json: Dict[str, Any], data_file_dir: str = DATA_FILE_DIR
) -> Dict[str, Union[str, Any]]:
    """Loads a data file."""
    path = request_json.get("path", "")
    if not path:
        logger.error("Path cannot be empty.")
        return {"error": "Path cannot be empty."}
    logger.debug("control=%s, path=%s", "load", path)
    with Session(engine) as session:
        file_metadata = db_interface.get_db_object_by_key(
            session, "file_metadata", "path", path
        )
        if file_metadata is None:
            logger.error("File metadata not found for path %s.", path)
            return {"error": f"File metadata not found for path {path}."}
        data_file_path = file_metadata.data_file_path
        data_file_full_path = os.path.join(data_file_dir, data_file_path)

        if not os.path.exists(data_file_full_path):
            logger.error("Data file not found for path %s.", data_file_path)
            return {"error": f"Data file not found for path {data_file_path}."}

        data, error = data_interface.load_data_file(
            data_file_path, file_metadata.data_file_type, data_file_dir
        )
        if error:
            logger.error(error)
            return {"error": error}
        return {**file_metadata.to_dict(), "data": data}


def upload(
    engine: Engine,
    request_files: Dict[str, Any],
    request_form: Dict[str, Any],
    data_file_dir: str = DATA_FILE_DIR,
) -> Dict[str, str]:
    """Upload a file to the visualizer."""
    if not "file" in request_files:
        logger.error("File not found in request.")
        return {"error": "File not found in request."}
    file = request_files["file"]
    if not file.filename:
        logger.error("File has no filename.")
        return {"error": "File has no filename."}

    extension = os.path.splitext(file.filename)[1].replace(".", "").lower()
    if extension not in SUPPORTED_FILE_TYPES:
        logger.error("File type %s is not supported.", extension)
        return {"error": f"File type {extension} is not supported."}

    if not "path" in request_form:
        logger.error("Path not found in request.")
        return {"error": "Path not found in request."}
    path = request_form["path"]

    with Session(engine) as session:
        file_metadata = db_interface.get_db_object_by_key(
            session, "file_metadata", "path", path
        )
        if file_metadata is not None:
            logger.error("Path %s already exists.", path)
            return {"error": f"Path {path} already exists."}

        data_filename = data_interface.new_data_file_path(extension, data_file_dir)
        full_path = os.path.join(data_file_dir, data_filename)

        logger.info("Upload file at %s. Saving data file to %s.", path, full_path)
        file.save(full_path)

        db_interface.create_or_get_file_metadata(
            session,
            {
                "name": os.path.basename(path),
                "path": path,
                "data_file_type": extension,
                "data_file_path": data_filename,
                "tags": [],
            },
        )
    return {}


# TODO: Update/save call
