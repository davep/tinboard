"""Provides a widget for displaying the bookmarks."""

##############################################################################
# Python imports.
from datetime import datetime
from json import loads, dumps
from typing import Any
from webbrowser import open as open_url
from typing_extensions import Self

##############################################################################
# Textual imports.
from textual.binding import Binding
from textual.reactive import var
from textual.widgets import OptionList
from textual.widgets.option_list import Option

##############################################################################
# Pinboard API imports.
from aiopinboard import API
from aiopinboard.bookmark import Bookmark as BookmarkData

##############################################################################
# Local imports.
from ..utils import bookmarks_file


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

    bookmarks: var[list[Bookmark]] = var([])
    """The list of all known bookmarks."""

    last_downloaded: var[datetime | None] = var(None)
    """When the bookmarks were last downloaded."""

    def action_visit(self) -> None:
        """Visit the highlighted bookmark."""
        if self.highlighted is not None:
            bookmark = self.get_option_at_index(self.highlighted)
            assert isinstance(bookmark, Bookmark)
            if bookmark.href:
                open_url(bookmark.href)

    @property
    def tags(self) -> list[str]:
        """All known tags in the current displayed set of bookmarks"""
        tags = set()
        for n in range(self.option_count):
            bookmark = self.get_option_at_index(n)
            assert isinstance(bookmark, Bookmark)
            tags |= set(bookmark.tags)
        return sorted(list(tags))

    @property
    def latest_modification(self) -> datetime | None:
        """The latest modification time found in all the bookmarks.

        If there are no bookmarks this will be `None`.
        """
        return (
            sorted([bookmark.last_modified for bookmark in self.bookmarks])[-1]
            if self.bookmarks
            else None
        )

    def show_bookmarks(
        self, bookmarks: list[Bookmark], description: str = "All"
    ) -> Self:
        """Show the given list of bookmarks."""
        self.border_title = f"{description} ({len(bookmarks)})"
        return self.clear_options().add_options(bookmarks)

    def show_all(self) -> None:
        """Show all bookmarks."""
        self.show_bookmarks(self.bookmarks)

    def show_public(self) -> None:
        """Show public bookmarks."""
        self.show_bookmarks(
            [bookmark for bookmark in self.bookmarks if bookmark.shared], "Public"
        )

    def show_private(self) -> None:
        """Show private bookmarks."""
        self.show_bookmarks(
            [bookmark for bookmark in self.bookmarks if not bookmark.shared], "Private"
        )

    def show_unread(self) -> None:
        """Show unread bookmarks."""
        self.show_bookmarks(
            [bookmark for bookmark in self.bookmarks if bookmark.unread], "Unread"
        )

    def show_read(self) -> None:
        """Show read bookmarks."""
        self.show_bookmarks(
            [bookmark for bookmark in self.bookmarks if not bookmark.unread], "Read"
        )

    def show_untagged(self) -> None:
        """Show untagged bookmarks."""
        self.show_bookmarks(
            [bookmark for bookmark in self.bookmarks if not bookmark.tags], "Untagged"
        )

    def show_tagged(self) -> None:
        """Show tagged bookmarks."""
        self.show_bookmarks(
            [bookmark for bookmark in self.bookmarks if bookmark.tags], "Tagged"
        )

    def _watch_bookmarks(self) -> None:
        """Refresh the display when all bookmarks are updated."""
        self.show_bookmarks(self.bookmarks)

    @property
    def as_json(self) -> dict[str, Any]:
        """All the bookmarks as a JSON-friendly list."""
        return {
            "last_downloaded": None
            if self.last_downloaded is None
            else self.last_downloaded.isoformat(),
            "bookmarks": [bookmark.as_json for bookmark in self.bookmarks],
        }

    def load_json(self, data: dict[str, Any]) -> None:
        """Load the bookmarks from the given JSON data.

        Args:
            data: The data to load.
        """
        self.last_downloaded = datetime.fromisoformat(data["last_downloaded"])
        self.bookmarks = [
            Bookmark.from_json(bookmark) for bookmark in data["bookmarks"]
        ]

    def load(self) -> bool:
        """Load the bookmarks from the local file."""
        if bookmarks_file().exists():
            self.load_json(loads(bookmarks_file().read_text(encoding="utf-8")))
            self.loading = False
            return True
        return False

    def save(self) -> Self:
        """Save the bookmarks to the local file."""
        bookmarks_file().write_text(dumps(self.as_json, indent=4), encoding="utf-8")
        return self

    async def download_all(self, api: API) -> Self:
        """Download all available bookmarks from the server.

        Args:
            api: The API to download via.
        """
        self.bookmarks = [
            Bookmark(bookmark)
            for bookmark in await api.bookmark.async_get_all_bookmarks()
        ]
        self.last_downloaded = datetime.now()
        return self


### bookmarks.py ends here
