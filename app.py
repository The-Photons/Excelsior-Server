# IMPORTS
import base64
import os

from flask import Flask, request, abort
from yaml import safe_load
from pathlib import Path

from src.io import list_items_in_dir, is_path_safe
from src.encrypt import get_key, encrypt, decrypt

# CONSTANTS
CONFIG_FILE = Path("config.yml")
SECRETS_FILE = Path("secrets.yml")

ENCRYPTED_EXTENSION = ".encrypted"

# SETUP
# Set up flask application
app = Flask(__name__)

# Get configuration
with open(CONFIG_FILE, "r") as config:
    config = safe_load(config)

# Get the secret key
key = get_key(SECRETS_FILE)


# ROUTES
# CRUD Operations
@app.route("/list-dir", methods=["GET"])
def list_dir():
    """
    Lists what is in the specified directory.
    Directory to list is to be specified using URL parameters.
    :return: List of items in the specified directory, along with their type.
    """

    url_params = request.args
    path = Path(config["files_dir"]) / url_params.get("path", "")
    return {"status": "ok", "content": list_items_in_dir(path)}


@app.route("/get-file/<path:unsafe_path>", methods=["GET"])
def get_file(unsafe_path: str):
    """
    Gets a file with the specified path.
    :param unsafe_path: Path to the file.
    :return: Dictionary containing two things. The first is the status -- `ok` or `not found`. If `ok` then the second
             is the Base64 content of the file.
    """

    # Add the files directory to the unsafe path
    unsafe_path = Path(config["files_dir"], f"{unsafe_path}{ENCRYPTED_EXTENSION}")

    # Check the requested path by the user
    if not is_path_safe(config["files_dir"], unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Try to get the file
    try:
        with open(path, "rb") as f:
            content = f.read()
    except FileNotFoundError:
        return {"status": "not found"}

    # Decrypt the file using the key
    content = decrypt(content, key)

    # Then encode the content in base64 and send it
    return {"status": "ok", "content": base64.b64encode(content).decode("utf-8")}


@app.route("/create-dir/<path:unsafe_path>", methods=["POST"])
def create_dir(unsafe_path: str):
    """
    Creates a new directory in the files' directory.
    :param unsafe_path: Path to create the directory.
    :return: Status of the creation -- `ok` or `fail`.
    """

    # Add the files directory to the unsafe path
    unsafe_path = Path(config["files_dir"], unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(config["files_dir"], unsafe_path):
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
    Creates a new file in the files' directory.
    The content of the file should be specified in Base64 using a POST form, with the key `content`.
    :param unsafe_path: Path to create the file.
    :return: Status of the creation -- `ok` or `not found`.
    """

    # Add the files directory to the unsafe path
    unsafe_path = Path(config["files_dir"], f"{unsafe_path}{ENCRYPTED_EXTENSION}")
    content = request.form.get("content")

    # Check the requested path by the user
    if not is_path_safe(config["files_dir"], unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Encrypt the content of the file
    content = base64.b64decode(content)
    content = encrypt(content, key)

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

    # Add the files directory to the unsafe path
    unsafe_path = Path(config["files_dir"], unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(config["files_dir"], unsafe_path):
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

    # Add the files directory to the unsafe path
    unsafe_path = Path(config["files_dir"], f"{unsafe_path}{ENCRYPTED_EXTENSION}")

    # Check the requested path by the user
    if not is_path_safe(config["files_dir"], unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Delete the directory
    try:
        os.remove(path)
        return {"status": "ok"}
    except OSError:
        return {"status": "fail"}
