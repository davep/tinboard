"""Utility code for dealing with the data."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# XDG imports.
from xdg_base_dirs import xdg_data_home


##############################################################################
def data_dir() -> Path:
    """The path to the data directory for the application.

    Returns:
        The path to the data directory for the application.

    Note:
        If the directory doesn't exist, it will be created as a side-effect
        of calling this functon.
    """
    (save_to := xdg_data_home() / "tinboard").mkdir(parents=True, exist_ok=True)
    return save_to


##############################################################################
def bookmarks_file() -> Path:
    """The path to the file that the local bookmarks are held in.

    Returns:
        The path to the bookmarks file.
    """
    return data_dir() / "bookmarks.json"


##############################################################################
def token_file() -> Path:
    """The file where the API token is held.

    Returns:
        The path to the token file.
    """
    return data_dir() / ".token"


### data.py ends here
