# IMPORTS
import os
from typing import Optional

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
            return f"{size / GIBIBYTE:.{dp}0f} GiB"
        if size / MEBIBYTE >= 1:
            return f"{size / MEBIBYTE:.{dp}0f} MiB"
        if size / KIBIBYTE >= 1:
            return f"{size / KIBIBYTE:.{dp}0f} KiB"
    else:
        if size / GIGABYTE >= 1:
            return f"{size / GIGABYTE:.{dp}0f} GB"
        if size / MEGABYTE >= 1:
            return f"{size / MEGABYTE:.{dp}0f} MB"
        if size / KILOBYTE >= 1:
            return f"{size / KILOBYTE:.{dp}0f} kB"
    return f"{size} B"


def list_items_in_dir(directory: os.PathLike[str], alternate_units: bool = False) -> Optional[list[dict[str, str]]]:
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

    # Now get the properties of the file
    items = []
    for file in dir_content:
        item_stats = os.stat(os.path.join(directory, file))
        item_type = "file"
        if os.path.isdir(os.path.join(directory, file)):
            item_type = "directory"
        items.append({
            "name": file,
            "type": item_type,
            "size": nice_file_size(item_stats.st_size, alternate_units=alternate_units)
        })

    # Don't care about cases when sorting
    return sorted(items, key=lambda item: f"{item['type']}-{item['name']}".lower())


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
