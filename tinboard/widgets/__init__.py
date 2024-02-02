"""Widgets used in the application."""

##############################################################################
# Local imports.
from .bookmarks import Bookmark, Bookmarks
from .details import Details
from .filters import Filters
from .tags import InlineTags, TagsMenu

##############################################################################
# Public symbols.
__all__ = [
    "Bookmark",
    "Bookmarks",
    "Details",
    "Filters",
    "InlineTags",
    "TagsMenu",
]

### __init__.py ends here
