"""Code relating to the data stored by the application."""

##############################################################################
# Local imports.
from .bookmarks import Bookmarks, bookmarks_file
from .config import load_configuration, save_configuration
from .exit_states import ExitStates
from .token import token_file

##############################################################################
# Exports.
__all__ = [
    "bookmarks_file",
    "Bookmarks",
    "ExitStates",
    "load_configuration",
    "save_configuration",
    "token_file",
]

### __init__.py ends here
