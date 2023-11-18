"""Code relating to the bookmarks file."""

##############################################################################
# Python imports.
from pathlib import Path

##############################################################################
# Local imports.
from .locations import data_dir


##############################################################################
def bookmarks_file() -> Path:
    """The path to the file that the local bookmarks are held in.

    Returns:
        The path to the bookmarks file.
    """
    return data_dir() / "bookmarks.json"


### bookmarks.py ends here
