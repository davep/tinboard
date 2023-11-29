"""Generic custom messages for the application."""

##############################################################################
# Local imports.
from .commands import EditBookmark, ToggleBookmarkRead, ToggleBookmarkPublic
from .tags import ShowAlsoTaggedWith, ShowTaggedWith

##############################################################################
# Exports.
__all__ = [
    "EditBookmark",
    "ShowAlsoTaggedWith",
    "ShowTaggedWith",
    "ToggleBookmarkPublic",
    "ToggleBookmarkRead",
]

### __init__.py ends here
