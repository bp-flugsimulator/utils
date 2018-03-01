"""
Functions for path modification.
"""
from utils.typecheck import ensure_type


def remove_trailing_path_seperator(path):
    """
    If the last character is a path seperator, then it will be removed.

    Arguments
    ----------
        path: string

    Returns
    -------
        string
    """
    ensure_type("path", path, str)

    if path and (path[-1] == '\\' or path[-1] == '/'):
        return path[:-1]
    else:
        return path
