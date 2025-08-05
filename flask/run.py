"""Module run launches the Flask backend."""

import os

import dir_tree_lib

from flask_cors import CORS
from flask import Flask, request


app = Flask(__name__)
CORS(app)

FILE_BASE_DIR = os.getenv("FILE_BASE_DIR", ".")


@app.route("/api/version")
def version():
    """Gets the version of the Flask backend."""
    with open("version", "r", encoding="utf-8") as f:
        return {"version": f.read()}


@app.route("/api/tree", methods=["POST"])
def tree_control():  # pylint: disable=too-many-return-statements
    """Handles tree control requests."""
    control = request.json.get("control", "")

    match control:
        case "list":
            return dir_tree_lib.list_tree(FILE_BASE_DIR)
        case "create":
            return dir_tree_lib.create_folder(request.json, FILE_BASE_DIR)
        case "delete":
            return dir_tree_lib.delete(request.json, FILE_BASE_DIR)
        case "move":
            return dir_tree_lib.move(request.json, FILE_BASE_DIR)
        case "load":
            return dir_tree_lib.load(request.json, FILE_BASE_DIR)
        case "copy":
            return dir_tree_lib.copy(request.json, FILE_BASE_DIR)
        case _:
            return {"error": f"Invalid control: {control}"}


@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Uploads a file."""
    return dir_tree_lib.upload(request.files, request.form, FILE_BASE_DIR)


if __name__ == "__main__":
    app.run(debug=True)
