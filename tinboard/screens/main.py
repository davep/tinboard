"""The main screen for the application."""

##############################################################################
# Python imports.
from webbrowser import open as open_url

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
def filter_binding(name: str) -> Binding:
    """Create a binding for one of the core filters.

    Args:
        name: The name of the filter.

    Returns:
        A binding for the filter.
    """
    return Binding(Menu.shortcut(name), f"show_{name.lower()}")


##############################################################################
class Main(Screen[None]):
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
        border-left: tall $accent;
        background: $panel;
    }

    Menu {
        height: 1fr;
        min-width: 25;
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
        Binding("f2", "goto_pinboard", "pinboard.in"),
        Binding("ctrl+r", "redownload", "Re-download"),
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
        with Horizontal():
            yield Menu()
            yield Bookmarks()
            yield Details()
        yield Footer()

    def on_mount(self) -> None:
        """Start the process of loading the bookmarks."""
        self.sub_title = "Loading..."
        bookmarks = self.query_one(Bookmarks)
        bookmarks.loading = True
        if bookmarks.load():
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

    @on(Bookmarks.Changed)
    def _bookmarks_changed(self) -> None:
        """Refresh the display when an update happens."""
        bookmarks = self.query_one(Bookmarks)
        bookmarks.loading = False
        self.query_one(Menu).refresh_options(bookmarks)

    @on(Bookmarks.OptionHighlighted, "Bookmarks")
    def refresh_details(self, event: Bookmarks.OptionHighlighted) -> None:
        """Show the details of a highlighted bookmark.

        Args:
            event: The event causing the refresh.
        """
        assert isinstance(event.option, Bookmark)
        self.query_one(Details).bookmark = event.option

    def action_goto_pinboard(self) -> None:
        """Open Pinbaord in the user's web browser."""
        open_url("https://pinboard.in")

    def action_redownload(self) -> None:
        """Freshly download the bookmarks."""
        self.sub_title = "Loading..."
        self.query_one(Menu).refresh_options()
        self.query_one(Bookmarks).loading = True
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
    @on(Details.ShowTaggedWith)
    def show_tagged_with(
        self, event: Menu.ShowTaggedWith | Details.ShowTaggedWith
    ) -> None:
        """Show all bookmarks tagged with a given tag.

        Args:
            event: The event that contains the tag to show.
        """
        self.query_one(Bookmarks).show_tagged_with(event.tag)

    @on(Menu.ShowAlsoTaggedWith)
    def show_also_tagged_with(self, event: Menu.ShowAlsoTaggedWith) -> None:
        """Add a tag to any current tag filter and show the matching bookmarks.

        Args:
            event: The event that contains the tag to add.
        """
        self.query_one(Bookmarks).show_also_tagged_with(event.tag)


### main.py ends here
