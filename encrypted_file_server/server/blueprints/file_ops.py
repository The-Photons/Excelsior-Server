# IMPORTS
import base64
import os
import shutil
from pathlib import Path

from flask import Blueprint, request, current_app, abort
from flask_login import login_required, current_user

from encrypted_file_server.server.src.io import get_items_in_dir, traverse_dir, is_path_safe

# BLUEPRINT DEFINITION
file_ops = Blueprint("file_ops", __name__)


# HELPER FUNCTIONS
def user_folder():
    """
    Gets the user folder.
    :return: Path to the user folder.
    """
    return Path(current_app.instance_path, current_user.username)


# ROUTES
@file_ops.route("/list-dir", methods=["GET"])
@login_required
def list_dir():
    """
    Lists what is in the specified directory.
    Directory to list is to be specified using URL parameters.
    :return: Dictionary containing the status of the operation and the list of items in the specified directory, along
             with their type.
    """

    # Get the path from the URL parameters
    url_params = request.args
    unsafe_path = url_params.get("path", "")
    alternate_units = url_params.get("alternate_units", False)

    try:
        alternate_units = bool(alternate_units)
    except ValueError:
        alternate_units = False

    # Now properly create the unsafe path WRT the files directory
    unsafe_path = Path(user_folder(), unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(user_folder(), unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path
    return {"status": "ok", "content": get_items_in_dir(path, alternate_units=alternate_units)}


@file_ops.route("/recursive-list-dir", methods=["GET"])
@login_required
def recursive_list_dir():
    """
    Lists what is in the specified directory recursively.
    Directory to list is to be specified using URL parameters.
    :return: Dictionary containing the status of the operation and the list of items in the specified directory, along
             with their type.
    """

    # Get the path from the URL parameters
    url_params = request.args
    unsafe_path = url_params.get("path", "")

    # Now properly create the unsafe path WRT the files directory
    unsafe_path = Path(user_folder(), unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(user_folder(), unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Get the items in the directory
    items = traverse_dir(path)

    # For each path, remove the "data/files" starting string
    items = [item[len(str(user_folder())):] for item in items]

    return {"status": "ok", "content": items}


@file_ops.route("/path-exists/<path:unsafe_path>", methods=["GET"])
@login_required
def path_exists(unsafe_path: str):
    """
    Checks whether there is a file or folder at the specified path.
    :param unsafe_path: Path to the (possible) file.
    :return: Dictionary containing two things. The first is the status -- `ok` or `error`. If `ok` then the second
             is a boolean, describing whether the file or folder exists or not.
    """

    # Add the data directory to the unsafe path
    unsafe_path = Path(user_folder(), unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(user_folder(), unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    return {"status": "ok", "exists": os.path.exists(path)}


@file_ops.route("/get-file/<path:unsafe_path>", methods=["GET"])
@login_required
def get_file(unsafe_path: str):
    """
    Gets a file with the specified path.
    :param unsafe_path: Path to the file.
    :return: Dictionary containing two things. The first is the status -- `ok` or `not found`. If `ok` then the second
             is the Base64 content of the file.
    """
    # TODO: What if file too big?

    # Add the data directory to the unsafe path
    unsafe_path = Path(user_folder(), unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(user_folder(), unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Try to get the file
    try:
        with open(path, "rb") as f:
            content = f.read()
    except FileNotFoundError as e:
        return {"status": "not found", "message": str(e)}

    # Then encode the content in base64 and send it
    return {"status": "ok", "content": base64.b64encode(content).decode("utf-8")}


@file_ops.route("/create-dir/<path:unsafe_path>", methods=["POST"])
@login_required
def create_dir(unsafe_path: str):
    """
    Creates a new directory in the data directory.
    :param unsafe_path: Path to create the directory.
    :return: Status of the creation -- `ok` or `fail`.
    """

    # Add the data directory to the unsafe path
    unsafe_path = Path(user_folder(), unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(user_folder(), unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Create all missing folders and the requested folder
    try:
        os.makedirs(path)
        return {"status": "ok"}
    except (FileNotFoundError, FileExistsError) as e:
        return {"status": "fail", "message": str(e)}


@file_ops.route("/create-file/<path:unsafe_path>", methods=["POST"])
@login_required
def create_file(unsafe_path: str):
    """
    Creates a new file in the data directory.
    The content of the file should be specified in Base64 using a POST form, with the key `content`.
    :param unsafe_path: Path to create the file.
    :return: Status of the creation -- `ok` or `not found`.
    """

    # Add the data directory to the unsafe path
    unsafe_path = Path(user_folder(), unsafe_path)
    content = request.form.get("content")

    # Check the requested path by the user
    if not is_path_safe(user_folder(), unsafe_path):
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
    except FileNotFoundError as e:
        return {"status": "not found", "message": str(e)}


@file_ops.route("/delete-item/<path:unsafe_path>", methods=["DELETE"])
@login_required
def delete_item(unsafe_path: str):
    """
    Deletes an item (i.e. file or directory).
    :param unsafe_path: Path to the item to delete.
    :return: Status of the deletion -- `ok` or `fail`.
    """

    # Add the data directory to the unsafe path
    unsafe_path = Path(user_folder(), unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(user_folder(), unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Delete the item
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return {"status": "ok"}
    except OSError as e:
        return {"status": "fail", "message": str(e)}
