"""Provides a widget for displaying the bookmarks."""

##############################################################################
# Textual imports.
from textual.widgets import OptionList
from textual.widgets.option_list import Option

##############################################################################
# Pinboard API imports.
from aiopinboard.bookmark import Bookmark as BookmarkData


##############################################################################
class Bookmark(Option):
    """An individual bookmark."""

    def __init__(self, bookmark: BookmarkData) -> None:
        """Initialise the bookmark."""
        self.hash = bookmark.hash
        """The hash of the bookmark"""
        self.href = bookmark.href
        """The HREF of the bookmark"""
        self.title = bookmark.title
        """The title of the bookmark."""
        self.description = bookmark.description
        """The description of the bookmark."""
        self.last_modified = bookmark.last_modified
        """The time the bookmark was last modified."""
        self.tags = bookmark.tags
        """The tags for the bookmark."""
        self.unread = bookmark.unread
        """The unread status of the bookmark."""
        self.shared = bookmark.shared
        """The flag to say if the bookmark is public or private."""
        super().__init__(bookmark.title, id=bookmark.hash)


##############################################################################
class Bookmarks(OptionList):
    """The list of bookmarks."""


### bookmarks.py ends here
