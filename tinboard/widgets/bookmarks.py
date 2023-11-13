"""Provides a widget for displaying the bookmarks."""

##############################################################################
# Python imports.
from datetime import datetime
from typing import cast, Any
from webbrowser import open as open_url

##############################################################################
# Textual imports.
from textual.binding import Binding
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

    @property
    def as_json(self) -> dict[str, Any]:
        """The bookmark as a JSON-friendly dictionary."""
        return {
            "hash": self.hash,
            "href": self.href,
            "title": self.title,
            "description": self.description,
            "last_modified": self.last_modified.isoformat(),
            "tags": self.tags,
            "unread": self.unread,
            "shared": self.shared,
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "Bookmark":
        """Create a bookmark from some JSON data.

        Args:
            data: The data to create the bookmark from.

        Returns:
            The `Bookmark` instance.
        """
        (data := data.copy())["last_modified"] = datetime.fromisoformat(
            data["last_modified"]
        )
        return cls(BookmarkData(**data))


##############################################################################
class Bookmarks(OptionList):
    """The list of bookmarks."""

    BINDINGS = [
        Binding("enter", "visit", "Visit"),
    ]

    def action_visit(self) -> None:
        """Visit the highlighted bookmark."""
        if self.highlighted is not None:
            bookmark = self.get_option_at_index(self.highlighted)
            assert isinstance(bookmark, Bookmark)
            if bookmark.href:
                open_url(bookmark.href)

    @property
    def tags(self) -> list[str]:
        """All known tags."""
        tags = set()
        for n in range(self.option_count):
            bookmark = self.get_option_at_index(n)
            assert isinstance(bookmark, Bookmark)
            tags |= set(bookmark.tags)
        return sorted(list(tags))

    @property
    def as_json(self) -> list[dict[str, Any]]:
        """The collection of bookmarks as a JSON-friendly list."""
        return [cast(Bookmark, bookmark).as_json for bookmark in self._options]

    def load_json(self, data: list[dict[str, Any]]) -> None:
        """Load the bookmarks from the given JSON data.

        Args:
            data: The data to load.
        """
        self.clear_options().add_options(
            [Bookmark.from_json(bookmark) for bookmark in data]
        )


### bookmarks.py ends here
