"""The main screen for the application."""

##############################################################################
# Textual imports.
from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Header

##############################################################################
# Pinboard API library.
from aiopinboard import API

##############################################################################
# Local imports.
from ..widgets import Bookmarks, Bookmark, Menu


##############################################################################
class Main(Screen):
    """The main application screen."""

    TITLE = "TinBoard"
    SUB_TITLE = "A pinboard.in client"

    CSS = """
    *:can-focus {
        border: none;
        border-left: tall $accent 50%;
    }

    *:focus {
        border: none;
        border-left: thick $accent;
    }

    Menu {
        height: 1fr;
    }

    Bookmarks {
        height: 1fr;
        width: 9fr
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
            yield Bookmarks(classes="focus")
        yield Footer()

    def on_mount(self) -> None:
        """Start the process of loading the bookmarks."""
        self.query_one(Bookmarks).loading = True
        self.get_bookmarks()

    @work
    async def get_bookmarks(self) -> None:
        """Get all the bookmarks from pinboard."""
        bookmarks = await self._api.bookmark.async_get_all_bookmarks()
        bookmarks_display = self.query_one(Bookmarks)
        bookmarks_display.loading = False
        bookmarks_display.add_options(Bookmark(bookmark) for bookmark in bookmarks)


### main.py ends here
