# IMPORTS
import os
from typing import Optional


# FUNCTIONS
def list_items_in_dir(directory: os.PathLike[str]) -> Optional[list[tuple[str, str]]]:
    """
    List all files in the given directory.
    :param directory: Directory to give the list of files of.
    :return: List of files in the given directory, or `None` if no files are found.
    """

    # First list all the things in the directory
    try:
        dir_content = os.listdir(directory)
    except FileNotFoundError:
        return None

    # Now determine what the types of things are
    items = []
    for thing in dir_content:
        item_type = "file"
        if os.path.isdir(os.path.join(directory, thing)):
            item_type = "directory"
        items.append((thing, item_type))

    return items


def is_path_safe(files_dir: os.PathLike[str], unsafe_path: os.PathLike[str]) -> bool:
    """
    Checks if the requested file path by the user is safe.
    :param files_dir: Path to the files' directory.
    :param unsafe_path: User requested path.
    :return: True if the path is safe and False otherwise.
    """

    # Get the real path of the files directory
    files_dir = os.path.realpath(files_dir)

    # Then check if the path has a common prefix being the files directory
    return os.path.commonprefix((os.path.realpath(unsafe_path), files_dir)) == files_dir
