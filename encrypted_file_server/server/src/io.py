# IMPORTS
import os
from pathlib import Path
from typing import Optional, Union, List

from encrypted_file_server.server.src.misc import natural_sort

# CONSTANTS
KILOBYTE = 1000
MEGABYTE = KILOBYTE * KILOBYTE
GIGABYTE = KILOBYTE * KILOBYTE * KILOBYTE

KIBIBYTE = 1024
MEBIBYTE = KIBIBYTE * KIBIBYTE
GIBIBYTE = KIBIBYTE * KIBIBYTE * KIBIBYTE


# FUNCTIONS
def nice_file_size(size: int, dp: int = 2, alternate_units: bool = False) -> str:
    """
    Converts a raw size in bytes into a nicer display text.
    :param size: Size of the file in bytes.
    :param dp: Number of decimal places to round the number of bytes.
    :param alternate_units: Use IEC 80000-13:2008 format instead of SI format (i.e., kibibytes, mebibytes, gibibytes
    instead of kilobytes, megabytes, gigabytes)
    :return: Nicer display format of the size.
    """

    if alternate_units:
        if size / GIBIBYTE >= 1:
            return f"{size / GIBIBYTE:.0{dp}f} GiB"
        if size / MEBIBYTE >= 1:
            return f"{size / MEBIBYTE:.0{dp}f} MiB"
        if size / KIBIBYTE >= 1:
            return f"{size / KIBIBYTE:.0{dp}f} KiB"
    else:
        if size / GIGABYTE >= 1:
            return f"{size / GIGABYTE:.0{dp}f} GB"
        if size / MEGABYTE >= 1:
            return f"{size / MEGABYTE:.0{dp}f} MB"
        if size / KILOBYTE >= 1:
            return f"{size / KILOBYTE:.0{dp}f} kB"
    return f"{size} B"


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


def get_items_in_dir(directory: os.PathLike[str], alternate_units: bool = False) -> Optional[list[dict[str, str]]]:
    """
    List all data in the given directory.
    :param directory: Directory to give the list of data of.
    :param alternate_units: Use IEC 80000-13:2008 format instead of SI format (i.e., kibibytes, mebibytes, gibibytes
    instead of kilobytes, megabytes, gigabytes)
    :return: List of data in the given directory, or `None` if no data are found.
    """

    # First list all the things in the directory
    try:
        dir_content = os.listdir(directory)
    except FileNotFoundError:
        return None

    # Now get the properties of the item
    items = []
    for item in dir_content:
        item_path = os.path.join(directory, item)
        if os.path.isfile(item_path):
            item_type = "file"
            file_size = os.stat(item_path).st_size
        else:
            item_type = "directory"
            file_size = get_dir_size(item_path)
        items.append({
            "name": item,
            "type": item_type,
            "size": nice_file_size(file_size, alternate_units=alternate_units)
        })

    # Don't care about cases when sorting
    return sorted(items, key=lambda x: natural_sort(f"{x['type']}-{x['name']}"))


def traverse_dir(directory: os.PathLike[str]) -> Optional[list[str]]:
    """
    Recursively list the items in the directory.

    :param directory: Directory to give the list of data of.
    :return: List of data in the given directory, or `None` if no data are found.
    """

    # First list all the things in the directory
    try:
        dir_content = os.listdir(directory)
    except FileNotFoundError:
        return None

    # Now get the properties of the item
    items = []
    for item in dir_content:
        item_path = Path(os.path.join(directory, item))
        add_item = True
        if os.path.isdir(item_path):
            sub_items = traverse_dir(item_path)
            if len(sub_items) != 0:
                items += sub_items
            else:
                add_item = False

        if add_item:
            items.append(str(item_path))

    # Don't care about cases when sorting
    return sorted(items)


def is_path_safe(files_dir: os.PathLike[str], unsafe_path: os.PathLike[str]) -> bool:
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
