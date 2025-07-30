"""Module run launches the Flask backend."""

import os

from flask_cors import CORS
from flask import Flask, jsonify, request

import dir_tree_lib

app = Flask(__name__)
CORS(app)

FILE_BASE_DIR = os.getenv("FILE_BASE_DIR", ".")


@app.route("/api/version")
def version():
    """Gets the version of the Flask backend."""
    with open("version", "r", encoding="utf-8") as f:
        return {"version": f.read()}


@app.route("/api/files")
def get_files():
    """Gets the files in the current directory."""
    structure = {}

    for root, dirs, files in os.walk(FILE_BASE_DIR):
        current = structure

        # Skip the base dir itself
        if root != FILE_BASE_DIR:
            # Get relative path from base dir
            rel_path = os.path.relpath(root, FILE_BASE_DIR)
            path_parts = rel_path.split(os.sep)

            # Build nested dict structure for folders
            for part in path_parts:
                if part not in current:
                    current[part] = {
                        "type": "folder",
                        "full-path": os.path.join(
                            *path_parts[: path_parts.index(part) + 1]
                        ),
                        "children": {},
                    }
                current = current[part]["children"]

        # Add files at current level
        for file in files:
            rel_file_path = os.path.relpath(os.path.join(root, file), FILE_BASE_DIR)
            current[file] = {"type": "file", "full-path": rel_file_path, "tags": []}

    return structure


@app.route("/api/tree", methods=["POST"])
def tree_control():
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
    return dir_tree_lib.upload(
        request.files["file"], request.form["path"], FILE_BASE_DIR
    )


if __name__ == "__main__":
    app.run(debug=True)
