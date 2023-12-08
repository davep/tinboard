"""The main screen for the application."""

##############################################################################
# Python imports.
from functools import partial
from webbrowser import open as open_url

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Rule

##############################################################################
# Pinboard API library.
from aiopinboard import API
from aiopinboard.bookmark import Bookmark as BookmarkData
from aiopinboard.errors import RequestError

##############################################################################
# Local imports.
from .bookmark_input import BookmarkInput
from .confirm import Confirm
from .help import Help
from ..commands import (
    BookmarkModificationCommands,
    CoreCommands,
    CoreFilteringCommands,
    TagCommands,
)
from ..data import token_file, bookmarks_file, ExitStates
from ..messages import (
    AddBookmark,
    EditBookmark,
    DeleteBookmark,
    ShowAlsoTaggedWith,
    ShowTaggedWith,
    ToggleBookmarkPublic,
    ToggleBookmarkRead,
)
from ..widgets import Bookmarks, Bookmark, Details, Filters, Tags


##############################################################################
def filter_binding(name: str) -> Binding:
    """Create a binding for one of the core filters.

    Args:
        name: The name of the filter.

    Returns:
        A binding for the filter.
    """
    return Binding(Filters.shortcut(name), f"show_{name.lower()}")


##############################################################################
class Main(Screen[None]):
    """The main application screen."""

    # pylint:disable=too-many-public-methods

    CONTEXT_HELP = """
    ## Application keys and commands

    The following keys and commands are available throughout the application:

    | Key | Command | Description |
    | - | - | - |
    | <kbd>F1</kbd> | `Help` | This help screen. |
    | <kbd>F2</kbd> | `Visit Pinboard` | Visit the main Pinboard website. |
    | <kbd>F12</kbd> | `Logout` | Forgot your API token and remove the local bookmark cache. |
    | <kbd>Ctrl</kbd>+<kbd>l</kbd> | `Redownload/refresh bookmarks` | Reload the local bookmarks from Pinboard. |
    | <kbd>Ctrl</kbd>+<kbd>q</kbd> | `Quit the application` | Shockingly... quit the application! |
    | <kbd>Ctrl</kbd>+<kbd>p</kbd> | | Show the command palette. |
    """

    TITLE = "Tinboard"
    SUB_TITLE = "A pinboard.in client"
    COMMANDS = {
        BookmarkModificationCommands,
        CoreCommands,
        CoreFilteringCommands,
        TagCommands,
    }

    CSS = """
    Main {
        layout: horizontal;
    }

    Main > .focus {
        border: none;
        border-left: tall $accent 50%;
        background: $boost;
    }

    Main > .focus:focus, Main > .focus:focus-within {
        border: none;
        border-left: tall $accent;
        background: $panel;
    }

    #menu {
        padding: 0;
        margin: 0;
        height: 1fr;
        min-width: 25;
    }

    #menu Filters {
        padding-left: 1;
    }

    #menu Tags {
        height: 1fr;
    }

    #menu Rule {
        height: 1;
        margin: 0 0 0 0;
        background: $boost;
        color: $accent 50%;
    }

    #menu:focus-within Rule {
        background: $boost;
        color: $accent;
    }

    Bookmarks {
        height: 1fr;
        width: 6fr;
    }

    Details {
        height: 1fr;
        width: 3fr;
        min-width: 30;
    }
    """

    BINDINGS = [
        filter_binding("All"),
        filter_binding("Public"),
        filter_binding("Private"),
        filter_binding("Unread"),
        filter_binding("Read"),
        filter_binding("Tagged"),
        filter_binding("Untagged"),
        Binding("f1", "help", "Help"),
        Binding("f2", "goto_pinboard", "pinboard.in"),
        Binding("f12", "logout", "Logout", show=False),
        Binding("ctrl+l", "redownload", "Reload"),
        Binding("escape", "escape"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, api_token: str) -> None:
        """Initialise the main screen.

        Args:
            api_token: The Pinboard API token.
        """
        super().__init__()
        self._api = API(api_token)

    def compose(self) -> ComposeResult:
        """Lay out the content of the screen."""
        yield Header()
        with Vertical(id="menu", classes="focus"):
            yield Filters()
            yield Rule()
            yield Tags()
        yield Bookmarks(classes="focus")
        yield Details(classes="focus")
        yield Footer()

    def on_mount(self) -> None:
        """Start the process of loading the bookmarks."""
        self.sub_title = "Loading..."
        bookmarks = self.query_one(Bookmarks)
        bookmarks.loading = True
        bookmarks.load()
        self.maybe_redownload()

    @work
    async def download_bookmarks(self) -> None:
        """Get all the bookmarks from pinboard.

        Note:
            As a side-effect of calling this method, the local copy of all
            the bookmarks will be overwritten.
        """
        (await self.query_one(Bookmarks).download_all(self._api)).save()

    @work
    async def maybe_redownload(self) -> None:
        """Redownload the bookmarks if they look newer on the server."""
        if last_download := self.query_one(Bookmarks).last_downloaded:
            if (
                await self._api.bookmark.async_get_last_change_datetime()
                > last_download
            ):
                self.notify(
                    "Bookmarks on the server appear newer; downloading a fresh copy."
                )
                self.action_redownload()
        else:
            self.notify("No local bookmarks found; checking with the server.")
            self.action_redownload()

    @on(Bookmarks.Changed)
    def _bookmarks_changed(self) -> None:
        """Refresh the display when an update happens."""
        bookmarks = self.query_one(Bookmarks)
        bookmarks.loading = False
        # Setting loading to True disables the widget, which is good.
        # However, setting loading to False means not being disabled is kind
        # of slow to happen. This means that the focus that's going to
        # happen in a moment (look below) will fail. call_next, call_later
        # and call_after_refresh on the focus all fail. A short set_timer
        # works but that feels icky. So... let's force the issue.
        bookmarks.disabled = False
        self.query_one("#menu Tags", Tags).show(bookmarks.tags)
        TagCommands.current_tags = list(bookmarks.tags)
        bookmarks.focus()

    @on(Bookmarks.OptionHighlighted, "Bookmarks")
    def refresh_details(self, event: Bookmarks.OptionHighlighted) -> None:
        """Show the details of a highlighted bookmark.

        Args:
            event: The event causing the refresh.
        """
        assert isinstance(event.option, Bookmark)
        self.query_one(Details).bookmark = event.option

    def action_help(self) -> None:
        """Show the help screen."""
        self.app.push_screen(Help(self))

    def action_goto_pinboard(self) -> None:
        """Open Pinbaord in the user's web browser."""
        open_url("https://pinboard.in")

    def _logout(self, confirmed: bool) -> None:
        """Process the logout confirmation.

        Args:
            confirmed: Was the logout confirmed by the user?
        """
        if confirmed:
            token_file().unlink(True)
            bookmarks_file().unlink(True)
            self.app.exit(ExitStates.TOKEN_FORGOTTEN)

    def action_logout(self) -> None:
        """Perform the logout action."""
        self.app.push_screen(
            Confirm(
                "Logout",
                "Remove the local copy of your API token and delete the local copy of all bookmarks?",
            ),
            callback=self._logout,
        )

    def action_redownload(self) -> None:
        """Freshly download the bookmarks."""
        self.sub_title = "Loading..."
        self.query_one("#menu Tags", Tags).show([])
        self.query_one(Bookmarks).loading = True
        self.download_bookmarks()

    def action_escape(self) -> None:
        """Give some context to banging the escape key."""
        if self.screen.focused is None:
            return
        if isinstance(self.screen.focused, Details) or isinstance(
            self.screen.focused.parent, Details
        ):
            self.query_one(Bookmarks).focus()
        elif isinstance(self.screen.focused, (Bookmarks, Tags)):
            self.query_one(Filters).focus()

    @on(Filters.ShowAll)
    def action_show_all(self) -> None:
        """Show all bookmarks."""
        self.query_one(Bookmarks).show_all()

    @on(Filters.ShowPublic)
    def action_show_public(self) -> None:
        """Show all public bookmarks."""
        self.query_one(Bookmarks).show_public()

    @on(Filters.ShowPrivate)
    def action_show_private(self) -> None:
        """Show all private bookmarks."""
        self.query_one(Bookmarks).show_private()

    @on(Filters.ShowUnread)
    def action_show_unread(self) -> None:
        """Show all unread bookmarks."""
        self.query_one(Bookmarks).show_unread()

    @on(Filters.ShowRead)
    def action_show_read(self) -> None:
        """Show all read bookmarks."""
        self.query_one(Bookmarks).show_read()

    @on(Filters.ShowUntagged)
    def action_show_untagged(self) -> None:
        """Show all untagged bookmarks."""
        self.query_one(Bookmarks).show_untagged()

    @on(Filters.ShowTagged)
    def action_show_tagged(self) -> None:
        """Show all tagged bookmarks."""
        self.query_one(Bookmarks).show_tagged()

    @on(ShowTaggedWith)
    def show_tagged_with(self, event: ShowTaggedWith) -> None:
        """Show all bookmarks tagged with a given tag.

        Args:
            event: The event that contains the tag to show.
        """
        self.query_one(Bookmarks).show_tagged_with(event.tag)

    @on(ShowAlsoTaggedWith)
    def show_also_tagged_with(self, event: ShowAlsoTaggedWith) -> None:
        """Add a tag to any current tag filter and show the matching bookmarks.

        Args:
            event: The event that contains the tag to add.
        """
        self.query_one(Bookmarks).show_also_tagged_with(event.tag)

    async def post_result(self, result: BookmarkData | None) -> None:
        """Handle the result of an edit of a bookmark.

        Args:
            result: The result data, or `None` if the edit was cancelled.
        """
        if result:
            try:
                await self._api.bookmark.async_add_bookmark(
                    url=result.href,
                    title=result.title,
                    description=result.description,
                    tags=result.tags,
                    shared=result.shared,
                    toread=result.unread,
                    replace=True,
                )
                self.query_one(Bookmarks).update_bookmark(result).save()
                self.notify("Bookmark saved.")
            except RequestError as error:
                self.app.bell()
                self.notify(
                    str(error),
                    title="Error saving bookmark data",
                    severity="error",
                    timeout=10,
                )
                self.app.push_screen(
                    BookmarkInput(result, known_tags=self.query_one(Bookmarks).tags),
                    callback=self.post_result,
                )

    @on(AddBookmark)
    def add(self) -> None:
        """Add a new bookmark."""
        self.app.push_screen(
            BookmarkInput(known_tags=self.query_one(Bookmarks).tags),
            callback=self.post_result,
        )

    @on(EditBookmark)
    def edit(self) -> None:
        """Edit the current bookmark, if there is one."""
        if (bookmark := self.query_one(Bookmarks).current_bookmark) is None:
            self.app.bell()
        else:
            self.app.push_screen(
                BookmarkInput(
                    bookmark.as_bookmark, known_tags=self.query_one(Bookmarks).tags
                ),
                callback=self.post_result,
            )

    async def _delete(self, bookmark: Bookmark, confirmed: bool) -> None:
        """Respond to the user's confirmation about a bookmark deletion.

        Args:
            bookmark: The bookmark to delete.
            confirmed: The decision the user made about deletion.
        """
        if confirmed:
            await self._api.bookmark.async_delete_bookmark(bookmark.href)
            self.query_one(Bookmarks).remove_bookmark(bookmark).save()
            self.notify("Bookmark deleted.", severity="warning")

    @on(DeleteBookmark)
    def delete(self) -> None:
        """Delete the current bookmark, if there is one."""
        if (bookmark := self.query_one(Bookmarks).current_bookmark) is None:
            self.app.bell()
        else:
            self.app.push_screen(
                Confirm(
                    "Delete?",
                    f"Are you sure you wish to delete this bookmark?\n\n[dim i]{bookmark.title}[/]",
                ),
                callback=partial(self._delete, bookmark),
            )

    @on(ToggleBookmarkRead)
    async def toggle_read(self) -> None:
        """Toggle the read/unread status of the current bookmark."""
        if (bookmark := self.query_one(Bookmarks).current_bookmark) is None:
            self.app.bell()
        else:
            bookmark.unread = not bookmark.unread
            await self.post_result(bookmark.as_bookmark)

    @on(ToggleBookmarkPublic)
    async def toggle_public(self) -> None:
        """Toggle the public/private status of the current bookmark."""
        if (bookmark := self.query_one(Bookmarks).current_bookmark) is None:
            self.app.bell()
        else:
            bookmark.shared = not bookmark.shared
            await self.post_result(bookmark.as_bookmark)


### main.py ends here
