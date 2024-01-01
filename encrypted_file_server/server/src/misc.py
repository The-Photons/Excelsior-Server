# IMPORTS
import re


# FUNCTIONS
def natural_sort(elem: str) -> list:
    """
    Natural sorting key function.
    :param elem: Element to be sorted.
    :return: List, representing the key value to be used for sorting.
    """
    return [(int(char) if char.isdigit() else char.lower()) for char in re.split("([0-9]+)", elem)]
