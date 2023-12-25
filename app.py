# IMPORTS
import base64
import json
import os

from flask import Flask, request, abort
from yaml import safe_load
from pathlib import Path

from src.io import list_items_in_dir, is_path_safe

# CONSTANTS
CONFIG_FILE = Path("config.yml")
SECRETS_FILE = Path("secrets.yml")

# SETUP
# Set up flask application
app = Flask(__name__)

# Get configuration
with open(CONFIG_FILE, "r") as config:
    config = safe_load(config)

# Check if the data and files directory exists
dataDir = Path(config["data_dir"])
if not os.path.isdir(dataDir):
    os.mkdir(dataDir)

filesDir = Path(dataDir, config["files_dir"])
if not os.path.isdir(filesDir):
    os.mkdir(filesDir)


# ROUTES
# Key transfer operations
@app.route("/get-encryption-params", methods=["GET"])
def get_encryption_parameters():
    """
    Gets the encryption parameters from the `encrypt_params_file` file.
    :return: Dictionary of the status of the operation and the encryption parameters.
    """

    # TODO: Handle missing AES key file
    with open(os.path.join(dataDir, config["encrypt_params_file"]), "r") as f:
        encryption_params = json.load(f)
        return {
            "status": "ok",
            "iv": encryption_params.get("iv", ""),
            "salt": encryption_params.get("salt", ""),
            "test_str": encryption_params.get("test_str", ""),
            "encrypted_key": encryption_params.get("encrypted_key", "")
        }


# CRUD operations
@app.route("/list-dir", methods=["GET"])
def list_dir():
    """
    Lists what is in the specified directory.
    Directory to list is to be specified using URL parameters.
    :return: Dictionary containing the status of the operation and the list of items in the specified directory, along
             with their type.
    """

    url_params = request.args
    unsafe_path = Path(filesDir, url_params.get("path", ""))
    if not is_path_safe(filesDir, unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path
    return {"status": "ok", "content": list_items_in_dir(path)}


@app.route("/get-file/<path:unsafe_path>", methods=["GET"])
def get_file(unsafe_path: str):
    """
    Gets a file with the specified path.
    :param unsafe_path: Path to the file.
    :return: Dictionary containing two things. The first is the status -- `ok` or `not found`. If `ok` then the second
             is the Base64 content of the file.
    """

    # Add the data directory to the unsafe path
    unsafe_path = Path(filesDir, unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(filesDir, unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Try to get the file
    try:
        with open(path, "rb") as f:
            content = f.read()
    except FileNotFoundError:
        return {"status": "not found"}

    # Then encode the content in base64 and send it
    return {"status": "ok", "content": base64.b64encode(content).decode("utf-8")}


@app.route("/create-dir/<path:unsafe_path>", methods=["POST"])
def create_dir(unsafe_path: str):
    """
    Creates a new directory in the data' directory.
    :param unsafe_path: Path to create the directory.
    :return: Status of the creation -- `ok` or `fail`.
    """

    # Add the data directory to the unsafe path
    unsafe_path = Path(filesDir, unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(filesDir, unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Create the folder
    try:
        os.mkdir(path)
        return {"status": "ok"}
    except FileNotFoundError:
        return {"status": "fail"}


@app.route("/create-file/<path:unsafe_path>", methods=["POST"])
def create_file(unsafe_path: str):
    """
    Creates a new file in the data' directory.
    The content of the file should be specified in Base64 using a POST form, with the key `content`.
    :param unsafe_path: Path to create the file.
    :return: Status of the creation -- `ok` or `not found`.
    """

    # Add the data directory to the unsafe path
    unsafe_path = Path(filesDir, unsafe_path)
    content = request.form.get("content")

    # Check the requested path by the user
    if not is_path_safe(filesDir, unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Decode the content of the file
    content = base64.b64decode(content)

    # Now save the file
    try:
        with open(path, "wb") as f:
            f.write(content)
            return {"status": "ok"}
    except FileNotFoundError:
        return {"status": "not found"}


@app.route("/delete-dir/<path:unsafe_path>", methods=["DELETE"])
def delete_dir(unsafe_path: str):
    """
    Deletes a directory.
    :param unsafe_path: Path to the directory to delete.
    :return: Status of the deletion -- `ok` or `fail`.
    """

    # Add the data directory to the unsafe path
    unsafe_path = Path(filesDir, unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(filesDir, unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Delete the directory
    try:
        os.rmdir(path)
        return {"status": "ok"}
    except OSError:
        return {"status": "fail"}


@app.route("/delete-file/<path:unsafe_path>", methods=["DELETE"])
def delete_file(unsafe_path: str):
    """
    Deletes a file.
    :param unsafe_path: Path to the file to delete.
    :return: Status of the deletion -- `ok` or `fail`.
    """

    # Add the data directory to the unsafe path
    unsafe_path = Path(filesDir, unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(filesDir, unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Delete the directory
    try:
        os.remove(path)
        return {"status": "ok"}
    except OSError:
        return {"status": "fail"}


# Miscellaneous operations
@app.route("/ping", methods=["GET"])
def ping():
    return {"status": "ok", "content": "pong"}
