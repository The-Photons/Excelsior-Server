# IMPORTS
import os
from typing import Optional

from encrypted_file_server.server.src.misc import natural_sort


# FUNCTIONS
def get_dir_size(path):
    """
    Get the full size of the directory.
    :param path: Path to the directory.
    :return: Total size of the directory.
    """
    total_size = 0
    for dir_path, _, filenames in os.walk(path):
        for file in filenames:
            file_path = os.path.join(dir_path, file)
            if not os.path.islink(file_path):
                total_size += os.path.getsize(file_path)

    return total_size


def get_items_in_dir(directory: str, prev_dir: str = "") -> Optional[list[dict[str, str]]]:
    """
    List all data in the given directory.
    :param directory: Directory to give the list of data of.
    :param prev_dir: Previous directory.
    :return: List of data in the given directory, or `None` if no data are found.
    """

    # First list all the things in the directory
    try:
        dir_content = os.listdir(directory)
    except FileNotFoundError:
        return None

    # Now get the properties of the item
    items = []
    for item_name in dir_content:
        item_abs_path = os.path.join(directory, item_name)
        item_rel_path = os.path.join(prev_dir, item_name)
        if os.path.isfile(item_abs_path):
            items.append({
                "name": item_name,
                "path": item_rel_path,
                "type": "file",
                "size": os.stat(item_abs_path).st_size
            })
        else:
            items.append({
                "name": item_name,
                "path": item_rel_path,
                "type": "directory",
                "items": get_items_in_dir(item_abs_path, prev_dir=os.path.join(prev_dir, item_name)),
                "size": get_dir_size(item_abs_path)
            })

    # Don't care about cases when sorting
    return sorted(items, key=lambda x: natural_sort(f"{x['type']}-{x['name']}"))


def is_path_safe(files_dir: str, unsafe_path: str) -> bool:
    """
    Checks if the requested file path by the user is safe.
    :param files_dir: Path to the data directory.
    :param unsafe_path: User requested path.
    :return: `True` if the path is safe and `False` otherwise.
    """

    # Get the real path of the data directory
    files_dir = os.path.realpath(files_dir)

    # Then check if the path has a common prefix being the data directory
    return os.path.commonprefix((os.path.realpath(unsafe_path), files_dir)) == files_dir
