# IMPORTS
import os
from typing import Optional


# FUNCTIONS
def list_items_in_dir(directory: os.PathLike[str]) -> Optional[list[tuple[str, str]]]:
    """
    List all data in the given directory.
    :param directory: Directory to give the list of data of.
    :return: List of data in the given directory, or `None` if no data are found.
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

    return sorted(items, key=lambda tpl: f"{tpl[1]}{tpl[0]}")


def is_path_safe(files_dir: os.PathLike[str], unsafe_path: os.PathLike[str]) -> bool:
    """
    Checks if the requested file path by the user is safe.
    :param files_dir: Path to the data' directory.
    :param unsafe_path: User requested path.
    :return: True if the path is safe and False otherwise.
    """

    # Get the real path of the data directory
    files_dir = os.path.realpath(files_dir)

    # Then check if the path has a common prefix being the data directory
    return os.path.commonprefix((os.path.realpath(unsafe_path), files_dir)) == files_dir
