"""The main screen for the application."""

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header

##############################################################################
# Pinboard API library.
from aiopinboard import API

##############################################################################
# Local imports.
from ..widgets import Bookmarks, Bookmark, Details, Menu


##############################################################################
class Main(Screen):
    """The main application screen."""

    TITLE = "TinBoard"
    SUB_TITLE = "A pinboard.in client"

    CSS = """
    *:can-focus {
        border: none;
        border-left: tall $accent 50%;
        background: $boost;
    }

    *:focus {
        border: none;
        border-left: thick $accent;
        background: $panel;
    }

    Menu {
        height: 1fr;
        min-width: 20;
    }

    Bookmarks {
        height: 1fr;
        width: 6fr;
        border-top: panel $accent 50% !important;
        border-title-align: center;
        border-title-color: $text;
    }

    Bookmarks:focus {
        border-top: panel $accent !important;
    }

    Details {
        height: 1fr;
        width: 3fr;
    }
    """

    BINDINGS = [
        Binding("a", "show_all", "All", key_display="a"),
        Binding("p", "show_public", "Public", key_display="p"),
        Binding("P", "show_private", "Private", key_display="P"),
        Binding("u", "show_unread", "Unread", key_display="u"),
        Binding("r", "show_read", "Read", key_display="r"),
        Binding("t", "show_tagged", "Tagged", key_display="t"),
        Binding("T", "show_untagged", "Untagged", key_display="T"),
        Binding("ctrl+r", "redownload", "Re-download"),
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
        with Horizontal():
            yield Menu()
            yield Bookmarks()
            yield Details()
        yield Footer()

    def _bookmarks_changed(self) -> None:
        """Refresh the display when an update happens."""
        bookmarks = self.query_one(Bookmarks)
        bookmarks.loading = False
        self.query_one(Menu).refresh_options(bookmarks)

    def on_mount(self) -> None:
        """Start the process of loading the bookmarks."""
        bookmarks = self.query_one(Bookmarks)
        bookmarks.border_title = "Loading..."
        bookmarks.loading = True
        if bookmarks.load():
            self._bookmarks_changed()
            self.maybe_redownload()
        else:
            self.download_bookmarks()

    @work
    async def download_bookmarks(self) -> None:
        """Get all the bookmarks from pinboard.

        Note:
            As a side-effect of calling this method, the local copy of all
            the bookmarks will be overwritten.
        """
        (await self.query_one(Bookmarks).download_all(self._api)).save()
        self._bookmarks_changed()

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

    @on(Bookmarks.OptionHighlighted, "Bookmarks")
    def refresh_details(self, event: Bookmarks.OptionHighlighted) -> None:
        """Show the details of a highlighted bookmark."""
        assert isinstance(event.option, Bookmark)
        self.query_one(Details).show(event.option)

    def action_redownload(self) -> None:
        """Freshly download the bookmarks."""
        self.query_one(Menu).refresh_options()
        bookmarks = self.query_one(Bookmarks)
        bookmarks.border_title = "Loading..."
        bookmarks.loading = True
        self.download_bookmarks()

    @on(Menu.ShowAll)
    def action_show_all(self) -> None:
        """Show all bookmarks."""
        self.query_one(Bookmarks).show_all()

    @on(Menu.ShowPublic)
    def action_show_public(self) -> None:
        """Show all public bookmarks."""
        self.query_one(Bookmarks).show_public()

    @on(Menu.ShowPrivate)
    def action_show_private(self) -> None:
        """Show all private bookmarks."""
        self.query_one(Bookmarks).show_private()

    @on(Menu.ShowUnread)
    def action_show_unread(self) -> None:
        """Show all unread bookmarks."""
        self.query_one(Bookmarks).show_unread()

    @on(Menu.ShowRead)
    def action_show_read(self) -> None:
        """Show all read bookmarks."""
        self.query_one(Bookmarks).show_read()

    @on(Menu.ShowUntagged)
    def action_show_untagged(self) -> None:
        """Show all untagged bookmarks."""
        self.query_one(Bookmarks).show_untagged()

    @on(Menu.ShowTagged)
    def action_show_tagged(self) -> None:
        """Show all tagged bookmarks."""
        self.query_one(Bookmarks).show_tagged()

    @on(Menu.ShowTaggedWith)
    def show_tagged_with(self, event: Menu.ShowTaggedWith) -> None:
        """Show all bookmarks tagged with a given tag."""
        self.query_one(Bookmarks).show_tagged_with(event.tag)


### main.py ends here
