"""Provides a widget for displaying the bookmarks."""

##############################################################################
# Python imports.
from collections import Counter
from datetime import datetime
from hashlib import md5
from json import loads, dumps
from typing import Any, Callable, cast
from webbrowser import open as open_url
from typing_extensions import Final, Self

##############################################################################
# pytz imports.
from pytz import UTC

##############################################################################
# Humanize imports.
from humanize import naturaltime

##############################################################################
# Textual imports.
from textual.binding import Binding
from textual.message import Message
from textual.reactive import var
from textual.widgets.option_list import Option, OptionDoesNotExist

##############################################################################
# Rich imports.
from rich.console import Group
from rich.emoji import Emoji
from rich.rule import Rule
from rich.table import Table

##############################################################################
# Pinboard API imports.
from aiopinboard import API
from aiopinboard.bookmark import Bookmark as BookmarkData

##############################################################################
# Local imports.
from ..messages import (
    AddBookmark,
    EditBookmark,
    DeleteBookmark,
    ToggleBookmarkPublic,
    ToggleBookmarkRead,
)
from ..data import bookmarks_file
from .extended_option_list import OptionListEx


##############################################################################
class Bookmark(Option):  # pylint:disable = too-many-instance-attributes
    """An individual bookmark."""

    PRIVATE_ICON: Final[str] = Emoji.replace(":lock:")
    """The icon to use for a private bookmark."""

    UNREAD_ICON: Final[str] = Emoji.replace(":see-no-evil_monkey:")
    """The icon to use for an unread bookmark."""

    def __init__(self, bookmark: BookmarkData) -> None:
        """Initialise the bookmark.

        Args:
            bookmark: The bookmark data gathered from the server.
        """
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
        super().__init__(self.prompt, id=bookmark.hash)

    @property
    def prompt(self) -> Group:
        """The prompt for the bookmark."""
        # Create the title and icons line.
        title = Table.grid(expand=True)
        title.add_column(ratio=1)
        title.add_column(justify="right")
        title.add_row(
            self.title,
            f"  {'' if self.shared else self.PRIVATE_ICON}{self.UNREAD_ICON if self.unread else ''}",
        )
        # Create the details line.
        details = Table.grid(expand=True)
        details.add_column(ratio=1)
        details.add_column()
        details.add_row(
            f"[dim][i]{naturaltime(self.last_modified)}[/][/]",
            f"[dim]{', '.join(sorted(self.tags, key = str.casefold))}[/]",
        )
        # Combine them and add a rule afterwards.
        return Group(title, details, Rule(style="dim"))

    def is_all(self, *checks: Callable[["Bookmark"], bool]) -> bool:
        """Does this bookmark pass all the given tests?

        Args:
            checks: The checks to run against the bookmark.

        Returns:
            `True` if all tests pass, `False` if not.
        """
        return all(check(self) for check in checks)

    def is_tagged(self, *tags: str) -> bool:
        """Is this bookmark tagged with the given tags?

        Args:
            tags: The tags to check for.

        Returns:
            `True` if the bookmark has all the tags, `False` if not.
        """
        return {tag.casefold() for tag in tags}.issubset(
            {tag.casefold() for tag in self.tags}
        )

    def has_text(self, search_text: str) -> bool:
        """Does the bookmark contain the given text?

        Note that this is a case-insensitive test.
        """
        return search_text.casefold() in (self.title + self.description).casefold()

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

    @property
    def as_bookmark(self) -> BookmarkData:
        """The bookmark as the underlying bookmark data."""
        data = self.as_json
        data["last_modified"] = datetime.fromisoformat(data["last_modified"])
        return BookmarkData(**data)

    def from_bookmark(self, bookmark: BookmarkData) -> None:
        """Update the bookmark from some bookmark data.

        Args:
            bookmark: The bookmark data to update from.
        """
        self.href = bookmark.href
        self.title = bookmark.title
        self.description = bookmark.description
        self.last_modified = bookmark.last_modified
        self.tags = bookmark.tags
        self.unread = bookmark.unread
        self.shared = bookmark.shared
        self.set_prompt(self.prompt)


##############################################################################
class Bookmarks(OptionListEx):  # pylint:disable = too-many-instance-attributes
    """The list of bookmarks."""

    # pylint:disable = too-many-public-methods

    CONTEXT_HELP = """
    ## Bookmarks keys and commands

    The following keys and commands are available in the bookmarks list:

    | Key | Command | Description |
    | - | - | - |
    | <kbd>Enter</kbd> | | Visit the current bookmark. |
    | <kbd>n</kbd> | `Add a new bookmark` | Create a new bookmark. |
    | <kbd>e</kbd> | `Edit bookmark` | Edit the currently-highlighted bookmark. |
    | <kbd>d</kbd> | `Delete bookmark` | Delete the currently-highlighted bookmark. |
    | <kbd>Ctrl</kbd>+<kbd>r</kbd> | `Toggle read/unread` | Toggle the read/unread status of the currently-highlighted bookmark. |
    | <kbd>Ctrl</kbd>+<kbd>v</kbd> | `Toggle public/private` | Toggle the visibility of the currently-highlighted bookmark. |
    """

    DEFAULT_CSS = """
    Bookmarks {
        scrollbar-gutter: stable;
    }

    Bookmarks > .option-list--option {
        padding: 0 1 0 1;
    }
    """

    BINDINGS = [
        Binding("enter", "visit", "Visit"),
        Binding("n", "new", "New"),
        Binding("e", "edit", "Edit"),
        Binding("d", "delete", "Delete"),
        Binding("ctrl+r", "read"),
        Binding("ctrl+v", "public"),
    ]

    bookmarks: var[list[Bookmark]] = var([], always_update=True)
    """The list of all known bookmarks."""

    last_downloaded: var[datetime | None] = var(None)
    """When the bookmarks were last downloaded."""

    read_filter: var[bool | None] = var(None)
    """The filter for the read status.

    `True` for read, `False` for unread, `None` for no filter.
    """

    public_filter: var[bool | None] = var(None)
    """The filter for the public status.

    `True` for public, `False` for private, `None` for no filter.
    """

    has_tags_filter: var[bool | None] = var(None)
    """The filter for if a bookmark has tags or not.

    `True` for has tags, `False` for doesn't have tags, `None` for no
    filter.
    """

    tag_filter: var[frozenset[str] | set[str]] = var(frozenset())
    """The tags to filter on."""

    text_filter: var[str] = var("")
    """The text to filter on. Empty string for no filter."""

    _suspend_refresh: var[bool] = var(False)
    """Flag to say if a refresh should be suspended."""

    def action_visit(self) -> None:
        """Visit the highlighted bookmark."""
        if self.highlighted is not None:
            bookmark = self.get_option_at_index(self.highlighted)
            assert isinstance(bookmark, Bookmark)
            if bookmark.href:
                open_url(bookmark.href)

    def action_new(self) -> None:
        """Post the new bookmark command."""
        self.post_message(AddBookmark())

    def action_edit(self) -> None:
        """Post the edit command."""
        self.post_message(EditBookmark())

    def action_delete(self) -> None:
        """Post the delete command."""
        self.post_message(DeleteBookmark())

    def action_read(self) -> None:
        """Post the read status toggle command."""
        self.post_message(ToggleBookmarkRead())

    def action_public(self) -> None:
        """Post the public/private toggle command."""
        self.post_message(ToggleBookmarkPublic())

    @property
    def tags(self) -> list[str]:
        """All known tags in the current displayed set of bookmarks"""
        tags: set[str] = set()
        for n in range(self.option_count):
            bookmark = self.get_option_at_index(n)
            assert isinstance(bookmark, Bookmark)
            tags |= set(tag for tag in bookmark.tags)
        return sorted(list(tags), key=str.casefold)

    @property
    def all_tags(self) -> list[str]:
        """All known tags for every saved bookmark."""
        tags: set[str] = set()
        for bookmark in self.bookmarks:
            tags |= set(tag for tag in bookmark.tags)
        return sorted(list(tags), key=str.casefold)

    @staticmethod
    def _tag_key(tag: tuple[str, int]) -> str:
        """Get the key for a tag/count pair.

        Args:
            tag: The tag information.

        Returns:
            The key to use when sorting the key.
        """
        return tag[0].casefold()

    @property
    def tag_counts(self) -> list[tuple[str, int]]:
        """All known tags in the current displayed set of bookmarks, with counts."""
        tags: list[str] = []
        for n in range(self.option_count):
            bookmark = self.get_option_at_index(n)
            assert isinstance(bookmark, Bookmark)
            tags.extend(bookmark.tags)
        return sorted(list(Counter(tags).items()), key=self._tag_key)

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

    class Changed(Message):
        """Message to say the visible collection of bookmarks has changed."""

    def _refresh_bookmarks(self) -> Self:
        """Refresh the display of bookmarks.

        Takes core filters and tags into account."""

        # GTFO if we're not supposed to refresh right now.
        if self._suspend_refresh:
            return self

        # Build up the filters.
        filter_names: list[str] = []
        filter_checks: list[Callable[[Bookmark], bool]] = []
        if self.public_filter is not None:
            filter_names.append("Public" if self.public_filter else "Private")
            filter_checks.append(lambda bookmark: bookmark.shared is self.public_filter)
        if self.read_filter is not None:
            filter_names.append("Read" if self.read_filter else "Unread")
            filter_checks.append(
                lambda bookmark: bookmark.unread is not self.read_filter
            )
        if self.has_tags_filter is not None:
            filter_names.append("Tagged" if self.has_tags_filter else "Untagged")
            filter_checks.append(
                lambda bookmark: bool(bookmark.tags) is self.has_tags_filter
            )
        if self.tag_filter:
            filter_names.append(f"Tagged {', '.join(sorted(self.tag_filter))}")
            filter_checks.append(lambda bookmark: bookmark.is_tagged(*self.tag_filter))
        if self.text_filter:
            filter_names.append(f"Contains '{self.text_filter}'")
            filter_checks.append(lambda bookmark: bookmark.has_text(self.text_filter))

        # Apply the filters.
        bookmarks = [
            bookmark for bookmark in self.bookmarks if bookmark.is_all(*filter_checks)
        ]

        # Set the title of the screen.
        # pylint:disable=attribute-defined-outside-init
        self.screen.sub_title = f"{'; '.join(filter_names) or 'All'} ({len(bookmarks)})"

        # Update the display of bookmarks, trying out best to keep the
        # currently-highlighted bookmark as the highlighted bookmark (if it
        # makes sense to, of course).
        highlighted_bookmark = (
            self.get_option_at_index(self.highlighted).id
            if self.highlighted is not None
            else None
        )
        try:
            return self.clear_options().add_options(bookmarks)
        finally:
            self.post_message(self.Changed())
            if bookmarks:
                try:
                    self.highlighted = self.get_option_index(
                        highlighted_bookmark or "--none--"
                    )
                except OptionDoesNotExist:
                    self.highlighted = 0

    def show_all(self) -> None:
        """Show all bookmarks."""
        # There's currently no way to prevent watch methods from being
        # triggered while updating reactives; and in this one situation I
        # really could do with not having them fire as I want to set default
        # values for a lot of reactives but only refresh the bookmarks the
        # once. So here I implement my own flag to make that happen.
        self._suspend_refresh = True
        try:
            self.public_filter = None
            self.read_filter = None
            self.has_tags_filter = None
            self.text_filter = ""
            self.tag_filter = frozenset()
        finally:
            self._suspend_refresh = False
            self._refresh_bookmarks()

    def _watch_read_filter(self) -> None:
        """React to the read/unread filer being changed."""
        self._refresh_bookmarks()

    def _watch_public_filter(self) -> None:
        """React to the public bookmark filter being changed."""
        self._refresh_bookmarks()

    def _watch_has_tags_filter(self) -> None:
        """React to the has tags filter being changed."""
        self._refresh_bookmarks()

    def _watch_text_filter(self) -> None:
        """React to the search text being changed."""
        self._refresh_bookmarks()

    def _validate_tag_filter(
        self, new_value: frozenset[str] | set[str]
    ) -> frozenset[str]:
        """Ensure the tags filter always ends up being a frozen set."""
        return new_value if isinstance(new_value, frozenset) else frozenset(new_value)

    def _watch_tag_filter(self) -> None:
        """React to the tags being changed."""
        self._refresh_bookmarks()

    def _watch_bookmarks(self) -> None:
        """Refresh the display when all bookmarks are updated."""
        self._refresh_bookmarks()

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
        self.last_downloaded = datetime.now(UTC)
        return self

    def _ensure_complete(self, data: BookmarkData) -> BookmarkData:
        """Ensure the bookmark data is complete.

        Args:
            data: The bookmark data to check.

        Returns:
            The bookmark data.

        When we add a new bookmark to Pinboard, we don't easily get back
        useful data like its hash. To get that it's necessary (and sort of
        costly) to query the bookmark back. Instead we fake it here. This is
        fine as we don't use this faked data to interact with Pinboard, we
        just use it internally to the app. Any subsequent refresh will
        overwrite anyway and then it'll all be fully in sync again.

        Moreover; this method uses the same hash-creation method that
        Pinboard appears to use (an md5 hex digest of the URL), so the
        'fake' hash should match the server anyway.
        """
        if not data.hash:
            data.hash = md5(data.href.encode()).hexdigest()
        return data

    def _add_bookmark(self, bookmark: BookmarkData) -> Self:
        """Add a bookmark we don't know about locally.

        Args:
            bookmark: The bookmark to add.

        Returns:
            Self.
        """
        self.bookmarks.insert(0, Bookmark(bookmark))
        self.bookmarks = self.bookmarks  # Force a watch.
        self.highlighted = 0
        # Assume this addition is the "last download" time. While it is true
        # that the user may have been editing in another client, or on the
        # web, meanwhile, in almost every case this will be the correct
        # approach to take *and* they can do a refresh if they want anyway.
        self.last_downloaded = datetime.now(UTC)
        return self

    def update_bookmark(self, new_data: BookmarkData) -> Self:
        """Update the details of the given bookmark.

        Args:
            new_data: The new data for the bookmark.

        Returns:
            Self.
        """

        try:
            bookmark = self.get_option(self._ensure_complete(new_data).hash)
        except OptionDoesNotExist:
            # We didn't find that bookmark; it must be new.
            return self._add_bookmark(new_data)

        # It's an existing bookmark so let's update it.
        assert isinstance(bookmark, Bookmark)
        bookmark.from_bookmark(new_data)
        self.replace_option_prompt(new_data.hash, bookmark.prompt)

        # Assume this edit is the "last download" time. While it is true
        # that the user may have been editing in another client, or on the
        # web, meanwhile, in almost every case this will be the correct
        # approach to take *and* they can do a refresh if they want anyway.
        self.last_downloaded = datetime.now(UTC)

        return self._refresh_bookmarks()

    def remove_bookmark(self, bookmark: Bookmark) -> Self:
        """Remove the given bookmark.

        Args:
            bookmark: The bookmark to remove.

        Returns:
            Self.
        """
        del self.bookmarks[self.bookmarks.index(bookmark)]
        self.bookmarks = self.bookmarks  # Force a watch.
        # Assume this deletion is the "last download" time. While it is true
        # that the user may have been editing in another client, or on the
        # web, meanwhile, in almost every case this will be the correct
        # approach to take *and* they can do a refresh if they want anyway.
        self.last_downloaded = datetime.now(UTC)
        return self

    @property
    def current_bookmark(self) -> Bookmark | None:
        """The currently-highlighted bookmark, if there is one."""
        if (bookmark := self.highlighted) is None:
            return None
        return cast(Bookmark, self.get_option_at_index(bookmark))


### bookmarks.py ends here
