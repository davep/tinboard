"""Provides a widget for displaying the bookmarks."""

##############################################################################
# Python imports.
from collections import Counter
from typing import Callable, Final, cast
from webbrowser import open as open_url

##############################################################################
# Humanize imports.
from humanize import naturaltime

##############################################################################
# Rich imports.
from rich.console import Group
from rich.emoji import Emoji
from rich.rule import Rule
from rich.table import Table

##############################################################################
# Textual imports.
from textual.app import DEFAULT_COLORS
from textual.binding import Binding
from textual.message import Message
from textual.reactive import var
from textual.widgets.option_list import Option, OptionDoesNotExist

##############################################################################
# Backward-compatible typing.
from typing_extensions import Self

##############################################################################
# Local imports.
from ..data import Bookmarks as LocalBookmarks
from ..messages import (
    AddBookmark,
    CheckWaybackMachine,
    CopyBookmarkURL,
    DeleteBookmark,
    EditBookmark,
    ToggleBookmarkPublic,
    ToggleBookmarkRead,
)
from ..pinboard import API, BookmarkData
from .extended_option_list import OptionListEx


##############################################################################
class Bookmark(Option):
    """An individual bookmark."""

    PRIVATE_ICON: Final[str] = Emoji.replace(":lock:")
    """The icon to use for a private bookmark."""

    UNREAD_ICON: Final[str] = Emoji.replace(":see-no-evil_monkey:")
    """The icon to use for an unread bookmark."""

    RULE: Final[Rule] = Rule(
        style=(
            DEFAULT_COLORS["dark"].accent.darken(0.15).rich_color.name
            if DEFAULT_COLORS["dark"].accent is not None
            else "blue"
        )
    )
    """The `Rule` to use between each bookmark."""

    def __init__(self, data: BookmarkData) -> None:
        """Initialise the bookmark.

        Args:
            data: The bookmark data gathered from the server.
        """
        self._data = data
        super().__init__(self.prompt, id=data.hash)

    @property
    def prompt(self) -> Group:
        """The prompt for the bookmark."""
        # Create the title and icons line.
        title = Table.grid(expand=True)
        title.add_column(ratio=1)
        title.add_column(justify="right")
        title.add_row(
            self._data.description,
            f"  {'' if self._data.shared else self.PRIVATE_ICON}{self.UNREAD_ICON if self._data.to_read else ''}",
        )
        # Create the details line.
        details = Table.grid(expand=True)
        details.add_column(ratio=1)
        details.add_column()
        details.add_row(
            f"[dim][i]{naturaltime(self._data.time)}[/][/]",
            f"[dim]{', '.join(sorted(self.data.tag_list, key = str.casefold))}[/]",
        )
        # Combine them and add a rule afterwards.
        return Group(title, details, self.RULE)

    @property
    def data(self) -> BookmarkData:
        """The bookmark as the underlying bookmark data."""
        return self._data

    @data.setter
    def data(self, data: BookmarkData) -> None:
        self._data = data
        self.set_prompt(self.prompt)


##############################################################################
class Bookmarks(OptionListEx):
    """The list of bookmarks."""

    CONTEXT_HELP = """
    ## Bookmarks keys and commands

    The following keys and commands are available in the bookmarks list:

    | Key | Command | Description |
    | - | - | - |
    | <kbd>Enter</kbd> | | Visit the current bookmark. |
    | <kbd>c</kbd> | `Copy to clipboard` | Copy the URL of the bookmark to the clipboard. |
    | <kbd>n</kbd> | `Add a new bookmark` | Create a new bookmark. |
    | <kbd>e</kbd> | `Edit bookmark` | Edit the currently-highlighted bookmark. |
    | <kbd>d</kbd> | `Delete bookmark` | Delete the currently-highlighted bookmark. |
    | <kbd>w</kbd> |  | Check if the bookmark is in the Wayback Machine. |
    | <kbd>Ctrl</kbd>+<kbd>r</kbd> | `Toggle read/unread` | Toggle the read/unread status of the currently-highlighted bookmark. |
    | <kbd>Ctrl</kbd>+<kbd>v</kbd> | `Toggle public/private` | Toggle the visibility of the currently-highlighted bookmark. |
    """

    DEFAULT_CSS = """
    Bookmarks {

        scrollbar-gutter: stable;

        .option-list--option {
            padding: 0 1 0 1;
        }
    }
    """

    BINDINGS = [
        Binding("enter", "visit", "Visit"),
        Binding("c", "copy"),
        Binding("n", "new", "New"),
        Binding("e", "edit", "Edit"),
        Binding("d", "delete", "Delete"),
        Binding("w", "check_wayback", "Wayback?"),
        Binding("ctrl+r", "read"),
        Binding("ctrl+v", "public"),
    ]

    bookmarks: var[LocalBookmarks] = var(LocalBookmarks, always_update=True, init=False)
    """The local copy of all the bookmarks."""

    read_filter: var[bool | None] = var(None, init=False)
    """The filter for the read status.

    `True` for read, `False` for unread, `None` for no filter.
    """

    public_filter: var[bool | None] = var(None, init=False)
    """The filter for the public status.

    `True` for public, `False` for private, `None` for no filter.
    """

    has_tags_filter: var[bool | None] = var(None, init=False)
    """The filter for if a bookmark has tags or not.

    `True` for has tags, `False` for doesn't have tags, `None` for no
    filter.
    """

    tag_filter: var[frozenset[str] | set[str]] = var(frozenset(), init=False)
    """The tags to filter on."""

    text_filter: var[str] = var("", init=False)
    """The text to filter on. Empty string for no filter."""

    _suspend_refresh: var[bool] = var(False)
    """Flag to say if a refresh should be suspended."""

    @property
    def highlighted_bookmark(self) -> Bookmark | None:
        """The currently-highlighted bookmark, if there is one."""
        if self.highlighted is not None:
            return cast(Bookmark, self.get_option_at_index(self.highlighted))
        return None

    def action_visit(self) -> None:
        """Visit the highlighted bookmark."""
        if (bookmark := self.highlighted_bookmark) is not None:
            if bookmark.data.href:
                open_url(bookmark.data.href)

    def action_copy(self) -> None:
        """Copy the URL of the current bookmark to the clipboard."""
        self.post_message(CopyBookmarkURL())

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

    async def action_check_wayback(self) -> None:
        """Check if the bookmark is in the Wayback Machine."""
        self.post_message(CheckWaybackMachine())

    @property
    def tags(self) -> list[str]:
        """All known tags in the current displayed set of bookmarks"""
        tags: set[str] = set()
        for n in range(self.option_count):
            bookmark = self.get_option_at_index(n)
            assert isinstance(bookmark, Bookmark)
            tags |= set(tag for tag in bookmark.data.tag_list)
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
            tags.extend(bookmark.data.tag_list)
        return sorted(list(Counter(tags).items()), key=self._tag_key)

    class Changed(Message):
        """Message to say the visible collection of bookmarks has changed."""

    def _refresh_bookmarks(self) -> Self:
        """Refresh the display of bookmarks.

        Takes core filters and tags into account.

        Returns:
            Self.
        """

        # GTFO if we're not supposed to refresh right now.
        if self._suspend_refresh:
            return self

        # Build up the filters.
        filter_names: list[str] = []
        filter_checks: list[Callable[[BookmarkData], bool]] = []
        if self.public_filter is not None:
            filter_names.append("Public" if self.public_filter else "Private")
            filter_checks.append(lambda bookmark: bookmark.shared is self.public_filter)
        if self.read_filter is not None:
            filter_names.append("Read" if self.read_filter else "Unread")
            filter_checks.append(
                lambda bookmark: bookmark.to_read is not self.read_filter
            )
        if self.has_tags_filter is not None:
            filter_names.append("Tagged" if self.has_tags_filter else "Untagged")
            filter_checks.append(
                lambda bookmark: bookmark.has_tags is self.has_tags_filter
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

        # Update the display of bookmarks, trying our best to keep the
        # currently-highlighted bookmark as the highlighted bookmark (if it
        # makes sense to, of course).
        highlighted_bookmark = (
            self.get_option_at_index(self.highlighted).id
            if self.highlighted is not None
            else None
        )
        try:
            return self.clear_options().add_options(
                Bookmark(bookmark) for bookmark in bookmarks
            )
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

    def load(self) -> Self:
        """Load the bookmarks from the local file.

        Returns:
            Self.
        """
        self.bookmarks = self.bookmarks.load()
        return self

    def save(self) -> Self:
        """Save the bookmarks to the local file."""
        self.bookmarks.save()
        return self

    async def download_all(self, api: API) -> Self:
        """Download all available bookmarks from the server.

        Args:
            api: The API to download via.

        Note:
            As a side-effect of calling this method, the local copy of all
            the bookmarks will be overwritten.

        Raises:
            API.RequestError: If there was an error downloading.
            OSError: If there was an error saving the bookmarks.
        """
        self.bookmarks = (await LocalBookmarks().download(api)).save()
        return self

    def update_bookmark(self, new_data: BookmarkData) -> Self:
        """Update the details of the given bookmark.

        Args:
            new_data: The new data for the bookmark.

        Returns:
            Self.
        """
        self.bookmarks.update_bookmark(new_data).mark_downloaded()
        return self._refresh_bookmarks()

    def remove_bookmark(self, bookmark: Bookmark) -> Self:
        """Remove the given bookmark.

        Args:
            bookmark: The bookmark to remove.

        Returns:
            Self.
        """
        self.bookmarks = self.bookmarks.remove_bookmark(bookmark.data).mark_downloaded()
        return self

    @property
    def current_bookmark(self) -> Bookmark | None:
        """The currently-highlighted bookmark, if there is one."""
        if (bookmark := self.highlighted) is None:
            return None
        return cast(Bookmark, self.get_option_at_index(bookmark))


### bookmarks.py ends here
