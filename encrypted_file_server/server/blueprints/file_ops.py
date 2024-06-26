# IMPORTS
import os
import shutil

from flask import Blueprint, request, current_app, abort, send_from_directory
from flask_login import login_required, current_user

from encrypted_file_server.server.src.io import get_items_in_dir, is_path_safe, get_dir_size

# BLUEPRINT DEFINITION
file_ops = Blueprint("file_ops", __name__, url_prefix="/file-ops")


# HELPER FUNCTIONS
def user_folder():
    """
    Gets the user folder.
    :return: Path to the user folder.
    """
    return os.path.join(current_app.instance_path, current_user.username)


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
    rel_path = url_params.get("path", "")

    # Now properly create the unsafe path WRT the files directory
    unsafe_abs_path = os.path.join(user_folder(), rel_path)

    # Check the requested path by the user
    if not is_path_safe(user_folder(), unsafe_abs_path):
        abort(403)

    # If reached here the path should be safe
    abs_path = unsafe_abs_path

    # Get the items in the directory
    items = get_items_in_dir(abs_path, prev_dir=rel_path)
    if items is None:
        return {"status": "not found"}

    return {
        "status": "ok",
        "name": os.path.basename(rel_path),
        "path": rel_path,
        "type": "directory",
        "items": items,
        "size": get_dir_size(abs_path)
    }


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
    unsafe_path = os.path.join(user_folder(), unsafe_path)

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
    :return: File content.
    """

    return send_from_directory(user_folder(), unsafe_path)


@file_ops.route("/create-dir/<path:unsafe_path>", methods=["POST"])
@login_required
def create_dir(unsafe_path: str):
    """
    Creates a new directory in the data directory.
    :param unsafe_path: Path to create the directory.
    :return: Status of the creation -- `ok` or `fail`.
    """

    # Add the data directory to the unsafe path
    unsafe_path = os.path.join(user_folder(), unsafe_path)

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
    :return: Status of the creation -- "ok" or "fail".
    """

    # Add the data directory to the unsafe path
    unsafe_path = os.path.join(user_folder(), unsafe_path)

    # Check the requested path by the user
    if not is_path_safe(user_folder(), unsafe_path):
        abort(403)

    # If reached here the path should be safe
    path = unsafe_path

    # Check that the POST request contains a file
    if "file" not in request.files:
        return {"status": "fail", "message": "No file part"}
    file = request.files["file"]
    if file.filename == "":
        return {"status": "fail", "message": "No file provided"}

    # Now save the file
    file.save(path)
    return {"status": "ok"}


@file_ops.route("/delete-item/<path:unsafe_path>", methods=["DELETE"])
@login_required
def delete_item(unsafe_path: str):
    """
    Deletes an item (i.e. file or directory).
    :param unsafe_path: Path to the item to delete.
    :return: Status of the deletion -- `ok` or `fail`.
    """

    # Add the data directory to the unsafe path
    unsafe_path = os.path.join(user_folder(), unsafe_path)

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
