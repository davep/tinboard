"""The main screen for the application."""

##############################################################################
# Python imports.
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

##############################################################################
# Local imports.
from .bookmark_input import BookmarkInput
from ..commands import CoreFilteringCommands, TagCommands
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

    TITLE = "TinBoard"
    SUB_TITLE = "A pinboard.in client"
    COMMANDS = {CoreFilteringCommands, TagCommands}

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
        Binding("f2", "goto_pinboard", "pinboard.in"),
        Binding("ctrl+r", "redownload", "Re-download"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("escape", "escape"),
        Binding("e", "edit", "Edit"),
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
        TagCommands.show_tagged = self.query_one(Bookmarks).show_tagged_with
        TagCommands.show_also_tagged = self.query_one(Bookmarks).show_also_tagged_with
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
        self.query_one("#menu Tags", Tags).show(bookmarks.tags)
        TagCommands.current_tags = list(bookmarks.tags)

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

    @on(Tags.ShowTaggedWith)
    def show_tagged_with(self, event: Tags.ShowTaggedWith) -> None:
        """Show all bookmarks tagged with a given tag.

        Args:
            event: The event that contains the tag to show.
        """
        self.query_one(Bookmarks).show_tagged_with(event.tag)

    @on(Tags.ShowAlsoTaggedWith)
    def show_also_tagged_with(self, event: Tags.ShowAlsoTaggedWith) -> None:
        """Add a tag to any current tag filter and show the matching bookmarks.

        Args:
            event: The event that contains the tag to add.
        """
        self.query_one(Bookmarks).show_also_tagged_with(event.tag)

    def edit_result(self, result: BookmarkData | None) -> None:
        """Handle the result of an edit of a bookmark.

        Args:
            result: The result data, or `None` if the edit was cancelled.
        """
        if result:
            self.notify("TODO: Use the result.")

    def action_edit(self) -> None:
        """Edit the current bookmark, if there is one."""
        bookmark = self.query_one(Bookmarks).highlighted
        if bookmark is None:
            self.app.bell()
        else:
            data = self.query_one(Bookmarks).get_option_at_index(bookmark)
            assert isinstance(data, Bookmark)
            self.app.push_screen(
                BookmarkInput(data.as_bookmark), callback=self.edit_result
            )


### main.py ends here
