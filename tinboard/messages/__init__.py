"""Generic custom messages for the application."""

##############################################################################
# Local imports.
from .commands import (
    AddBookmark,
    EditBookmark,
    ToggleBookmarkRead,
    ToggleBookmarkPublic,
)
from .tags import ShowAlsoTaggedWith, ShowTaggedWith

##############################################################################
# Exports.
__all__ = [
    "AddBookmark",
    "EditBookmark",
    "ShowAlsoTaggedWith",
    "ShowTaggedWith",
    "ToggleBookmarkPublic",
    "ToggleBookmarkRead",
]

### __init__.py ends here
