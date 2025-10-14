"""Module run launches the Flask backend."""

import os

import dir_tree_lib
from db import db_interface

from flask_cors import CORS
from flask import Flask, request

VERSION_FILE = os.environ.get("VERSION_FILE", os.path.join("flask", "version"))

app = Flask(__name__)
CORS(app)


@app.route("/api/version")
def version():
    """Gets the version of the Flask backend."""
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        return {"version": f.read()}


@app.route("/api/tree", methods=["POST"])
def tree_control():  # pylint: disable=too-many-return-statements
    """Handles tree control requests."""
    control = request.json.get("control", "")

    match control:
        case "list":
            return dir_tree_lib.list_tree(
                db_interface.make_engine(dir_tree_lib.DB_PATH)
            )
        case "delete":
            return dir_tree_lib.tree_delete(
                db_interface.make_engine(dir_tree_lib.DB_PATH),
                request.json,
                data_file_dir=dir_tree_lib.DATA_FILE_DIR,
            )
        case "move":
            return dir_tree_lib.move(
                db_interface.make_engine(dir_tree_lib.DB_PATH), request.json
            )
        case "load":
            return dir_tree_lib.load(
                db_interface.make_engine(dir_tree_lib.DB_PATH),
                request.json,
                data_file_dir=dir_tree_lib.DATA_FILE_DIR,
            )
        case "copy":
            return dir_tree_lib.copy(
                db_interface.make_engine(dir_tree_lib.DB_PATH), request.json
            )
        case "update":
            return dir_tree_lib.update(
                db_interface.make_engine(dir_tree_lib.DB_PATH), request.json
            )
        case _:
            return {"error": f"Invalid control: {control}"}


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Uploads a file."""
    return dir_tree_lib.upload(
        db_interface.make_engine(dir_tree_lib.DB_PATH),
        request.files,
        request.form,
        data_file_dir=dir_tree_lib.DATA_FILE_DIR,
    )


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True)
