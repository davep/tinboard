"""Functions for getting the locations of data."""

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


### locations.py ends here
