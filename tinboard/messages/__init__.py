"""Generic custom messages for the application."""

##############################################################################
# Local imports.
from .commands import (
    AddBookmark,
    EditBookmark,
    DeleteBookmark,
    ToggleBookmarkRead,
    ToggleBookmarkPublic,
)
from .tags import ClearTags, ShowAlsoTaggedWith, ShowTaggedWith

##############################################################################
# Exports.
__all__ = [
    "AddBookmark",
    "ClearTags",
    "EditBookmark",
    "DeleteBookmark",
    "ShowAlsoTaggedWith",
    "ShowTaggedWith",
    "ToggleBookmarkPublic",
    "ToggleBookmarkRead",
]

### __init__.py ends here
