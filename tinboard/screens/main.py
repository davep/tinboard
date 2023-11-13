"""The main screen for the application."""

##############################################################################
# Python imports.
from json import dumps, loads

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
from ..utils import bookmarks_file


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

    def on_mount(self) -> None:
        """Start the process of loading the bookmarks."""
        self.query_one(Bookmarks).border_title = "Loading..."
        self.query_one(Bookmarks).loading = True
        # TODO: a lot of tidying up of this. This is just an iterative step
        # towards where I want to be.
        if bookmarks_file().exists():
            self.query_one(Bookmarks).load_json(
                loads(bookmarks_file().read_text(encoding="utf-8"))
            )
            self.query_one(Bookmarks).loading = False
            self.query_one(Bookmarks).border_title = "All"
            self.query_one(Menu).refresh_options(self.query_one(Bookmarks))
        else:
            self.get_bookmarks()

    @work
    async def get_bookmarks(self) -> None:
        """Get all the bookmarks from pinboard."""
        bookmarks = await self._api.bookmark.async_get_all_bookmarks()
        bookmarks_display = self.query_one(Bookmarks)
        bookmarks_display.loading = False
        bookmarks_display.add_options(Bookmark(bookmark) for bookmark in bookmarks)
        bookmarks_display.border_title = "All"
        self.query_one(Menu).refresh_options(bookmarks_display)
        # Temporary write of the bookmarks to a file. I'm going to make this
        # a lot smarter; this will be using a local cache with a check of
        # last update, and all that, but for now I just want to get saving
        # going to check it's all making sense.
        bookmarks_file().write_text(dumps(bookmarks_display.as_json, indent=4))

    @on(Bookmarks.OptionHighlighted, "Bookmarks")
    def refresh_details(self, event: Bookmarks.OptionHighlighted) -> None:
        """Show the details of a highlighted bookmark."""
        assert isinstance(event.option, Bookmark)
        self.query_one(Details).show(event.option)


### main.py ends here
