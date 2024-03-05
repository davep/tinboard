"""Generic custom messages for the application."""

##############################################################################
# Local imports.
from .commands import (
    AddBookmark,
    Command,
    CopyBookmarkURL,
    DeleteBookmark,
    EditBookmark,
    ToggleBookmarkPublic,
    ToggleBookmarkRead,
)
from .tags import ClearTags, ShowAlsoTaggedWith, ShowTaggedWith

##############################################################################
# Exports.
__all__ = [
    "AddBookmark",
    "ClearTags",
    "Command",
    "CopyBookmarkURL",
    "EditBookmark",
    "DeleteBookmark",
    "ShowAlsoTaggedWith",
    "ShowTaggedWith",
    "ToggleBookmarkPublic",
    "ToggleBookmarkRead",
]

### __init__.py ends here
