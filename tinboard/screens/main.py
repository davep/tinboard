"""The main screen for the application."""

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
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
            # TODO: look for newer stuff.
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

    @on(Bookmarks.OptionHighlighted, "Bookmarks")
    def refresh_details(self, event: Bookmarks.OptionHighlighted) -> None:
        """Show the details of a highlighted bookmark."""
        assert isinstance(event.option, Bookmark)
        self.query_one(Details).show(event.option)

    @on(Menu.ShowAll)
    def show_all(self) -> None:
        """Show all bookmarks."""
        self.query_one(Bookmarks).show_all()

    @on(Menu.ShowPublic)
    def show_public(self) -> None:
        """Show all public bookmarks."""
        self.query_one(Bookmarks).show_public()

    @on(Menu.ShowPrivate)
    def show_private(self) -> None:
        """Show all private bookmarks."""
        self.query_one(Bookmarks).show_private()

    @on(Menu.ShowUnread)
    def show_unread(self) -> None:
        """Show all unread bookmarks."""
        self.query_one(Bookmarks).show_unread()

    @on(Menu.ShowRead)
    def show_read(self) -> None:
        """Show all read bookmarks."""
        self.query_one(Bookmarks).show_read()

    @on(Menu.ShowUntagged)
    def show_untagged(self) -> None:
        """Show all untagged bookmarks."""
        self.query_one(Bookmarks).show_untagged()

    @on(Menu.ShowTagged)
    def show_tagged(self) -> None:
        """Show all tagged bookmarks."""
        self.query_one(Bookmarks).show_tagged()


### main.py ends here
