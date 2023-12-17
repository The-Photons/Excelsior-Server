# IMPORTS
import os.path

from flask import Flask, request, send_from_directory, send_file, abort
from yaml import safe_load
from pathlib import Path

from src.io import list_items_in_dir, is_path_safe

# CONSTANTS
CONFIG_FILE = "config.yml"

# SETUP
# Set up flask application
app = Flask(__name__)

# Get configuration
with open(CONFIG_FILE, "r") as f:
    config = safe_load(f)


# ROUTES
@app.route("/list-dir")
def list_dir():
    url_params = request.args
    path = Path(config["files_dir"]) / url_params.get("path", "")
    return list_items_in_dir(path)


@app.route("/get-file/<path:unsafe_path>")
def get_file(unsafe_path):
    # Add the files directory to the unsafe path
    unsafe_path = Path(config["files_dir"], unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(config["files_dir"], unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Then try to send the file
    try:
        return send_file(path)
    except FileNotFoundError as e:
        return str(e)
