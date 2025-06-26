"""Module run launches the Flask backend."""

from flask_cors import CORS
from flask import Flask

app = Flask(__name__)
CORS(app)


@app.route("/api/version")
def version():
    """Gets the version of the Flask backend."""
    with open("version", "r", encoding="utf-8") as f:
        return {"version": f.read()}


if __name__ == "__main__":
    app.run(debug=True)
