"""The main screen for the application."""

##############################################################################
# Python imports.
from functools import partial
from webbrowser import open as open_url

##############################################################################
# Pyperclip imports.
from pyperclip import copy as to_clipboard, PyperclipException

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Rule

##############################################################################
# Local imports.
from .. import __version__
from .bookmark_input import BookmarkInput
from .confirm import Confirm
from .help import Help
from .search_input import SearchInput
from ..commands import (
    BookmarkCommands,
    CoreCommands,
    CoreFilteringCommands,
    TagCommands,
)
from ..data import (
    load_configuration,
    save_configuration,
    token_file,
    bookmarks_file,
    ExitStates,
)
from ..messages import (
    AddBookmark,
    CopyBookmarkURL,
    ClearTags,
    DeleteBookmark,
    EditBookmark,
    ShowAlsoTaggedWith,
    ShowTaggedWith,
    ToggleBookmarkPublic,
    ToggleBookmarkRead,
)
from ..pinboard import API, BookmarkData
from ..widgets import Bookmarks, Bookmark, Details, Filters, TagsMenu


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

    CONTEXT_HELP = """
    ## Application keys and commands

    The following keys and commands are available throughout the application:

    | Key | Command | Description |
    | - | - | - |
    | <kbd>F1</kbd> | `Help` | This help screen. |
    | <kbd>F2</kbd> | `Visit Pinboard` | Visit the main Pinboard website. |
    | <kbd>F3</kbd> | | Toggle the bookmark details pane. |
    | <kbd>F4</kbd> | | Toggle the sort order of the tags menu. |
    | <kbd>F12</kbd> | `Logout` | Forgot your API token and remove the local bookmark cache. |
    | <kbd>Ctrl</kbd>+<kbd>l</kbd> | `Redownload/refresh bookmarks` | Reload the local bookmarks from Pinboard. |
    | <kbd>Ctrl</kbd>+<kbd>q</kbd> | `Quit the application` | Shockingly... quit the application! |
    | <kbd>Ctrl</kbd>+<kbd>p</kbd> | | Show the command palette. |
    | <kbd>/</kbd> | | Text search. |
    | <kbd>#</kbd> | | Focus the menu of tags. |
    | <kbd>a</kbd> | `Show All` | Show all bookmarks. |
    | <kbd>R</kbd> | `Show Unread` | Show all unread bookmarks. |
    | <kbd>r</kbd> | `Show Read` | Show all read bookmarks. |
    | <kbd>P</kbd> | `Show Private` | Show all private bookmarks. |
    | <kbd>p</kbd> | `Show Public` | Show all public bookmarks. |
    | <kbd>T</kbd> | `Show Untagged` | Show all untagged bookmarks. |
    | <kbd>t</kbd> | `Show Tagged` | Show all tagged bookmarks. |
    """

    TITLE = f"Tinboard v{__version__}"
    SUB_TITLE = "A pinboard.in client"
    COMMANDS = {
        BookmarkCommands,
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
        width: 2fr;
        height: 1fr;
        min-width: 28;

        Filters {
            padding-left: 1;
        }

        TagsMenu {
            height: 1fr;
        }

        Rule {
            height: 1;
            margin: 0 0 0 0;
            background: $boost;
            color: $accent 50%;
        }
    }

    #menu:focus-within Rule {
        background: $boost;
        color: $accent;
    }

    Bookmarks {
        height: 1fr;
        width: 5fr;
    }

    Details {
        height: 1fr;
        width: 3fr;
        min-width: 30;
    }

    /* Tweaks to the above when the details are hidden. */

    Main.details-hidden Details {
        display: none;
    }

    Main.details-hidden Bookmarks {
        width: 8fr;
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
        Binding("f2", "goto_pinboard"),
        Binding("f3", "toggle_details"),
        Binding("f4", "toggle_tag_order"),
        Binding("f12", "logout"),
        Binding("ctrl+l", "redownload"),
        Binding("escape", "escape"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("#", "focus('tags-menu')"),
        Binding("/", "search"),
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
            yield TagsMenu(id="tags-menu")
        yield Bookmarks(classes="focus")
        yield Details(classes="focus")
        yield Footer()

    def on_mount(self) -> None:
        """Start the process of loading the bookmarks."""
        configuration = load_configuration()
        self.set_class(not configuration.details_visible, "details-hidden")
        self.sub_title = "Loading cached bookmarks..."
        self.query_one(Bookmarks).loading = True
        self.query_one(TagsMenu).sort_by_count = configuration.sort_tags_by_count
        self.load_bookmarks()

    @work(thread=True)
    def load_bookmarks(self) -> None:
        """Load the local copy of the bookmarks, if they exist."""
        self.query_one(Bookmarks).load()
        self.app.call_from_thread(self.maybe_redownload)

    @work
    async def download_bookmarks(self) -> None:
        """Get all the bookmarks from Pinboard.

        Note:
            As a side-effect of calling this method, the local copy of all
            the bookmarks will be overwritten.
        """
        try:
            (await self.query_one(Bookmarks).download_all(self._api)).save()
        except API.RequestError:
            self.app.bell()
            self.notify(
                "Error downloading bookmarks from the server.",
                title="Download Error",
                severity="error",
                timeout=8,
            )
            self._bookmarks_changed()
        except OSError as error:
            self.app.bell()
            self.notify(
                f"Error saving the bookmarks.\n\n{error}",
                title="Save Error",
                severity="error",
                timeout=8,
            )

    @work
    async def maybe_redownload(self) -> None:
        """Redownload the bookmarks if they look newer on the server."""
        if last_download := self.query_one(Bookmarks).last_downloaded:
            try:
                latest_on_server = await self._api.last_update()
            except API.Error:
                self.app.bell()
                self.notify(
                    "Unable to get the last change date from Pinboard. Is your token valid?",
                    title="Server Error",
                    severity="error",
                    timeout=8,
                )
                return
            if latest_on_server > last_download:
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
        self.query_one(TagsMenu).show(bookmarks.tag_counts)
        TagCommands.current_tags = list(bookmarks.tags)
        self.query_one(Details).bookmark = bookmarks.current_bookmark
        # TODO: if getting the counts starts to look like it causes a wee
        # pause, perhaps calculate them from within a threaded worker.
        # Mostly though, so far, I'm not seeing any impact.
        self.query_one(Filters).counts = bookmarks.counts
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

    def action_toggle_details(self) -> None:
        """Toggle the display of the details pane."""
        self.toggle_class("details-hidden")
        config = load_configuration()
        config.details_visible = not self.has_class("details-hidden")
        save_configuration(config)

    def action_toggle_tag_order(self) -> None:
        """Toggle the ordering of the tags in the tag menu."""
        tags = self.query_one(TagsMenu)
        tags.sort_by_count = not tags.sort_by_count
        tags.show(self.query_one(Bookmarks).tag_counts)
        config = load_configuration()
        config.sort_tags_by_count = tags.sort_by_count
        save_configuration(config)

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
        self.query_one(TagsMenu).show([])
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
        elif isinstance(self.screen.focused, (Bookmarks, TagsMenu)):
            self.query_one(Filters).focus()

    @on(Filters.ShowAll)
    def action_show_all(self) -> None:
        """Show all bookmarks."""
        self.query_one(Bookmarks).show_all()

    @on(Filters.ShowPublic)
    def action_show_public(self) -> None:
        """Show all public bookmarks."""
        self.query_one(Bookmarks).public_filter = (
            None if self.query_one(Bookmarks).public_filter is True else True
        )

    @on(Filters.ShowPrivate)
    def action_show_private(self) -> None:
        """Show all private bookmarks."""
        self.query_one(Bookmarks).public_filter = (
            None if self.query_one(Bookmarks).public_filter is False else False
        )

    @on(Filters.ShowUnread)
    def action_show_unread(self) -> None:
        """Show all unread bookmarks."""
        self.query_one(Bookmarks).read_filter = (
            None if self.query_one(Bookmarks).read_filter is False else False
        )

    @on(Filters.ShowRead)
    def action_show_read(self) -> None:
        """Show all read bookmarks."""
        self.query_one(Bookmarks).read_filter = (
            None if self.query_one(Bookmarks).read_filter is True else True
        )

    @on(Filters.ShowUntagged)
    def action_show_untagged(self) -> None:
        """Show all untagged bookmarks."""
        self.query_one(Bookmarks).has_tags_filter = (
            None if self.query_one(Bookmarks).has_tags_filter is False else False
        )

    @on(Filters.ShowTagged)
    def action_show_tagged(self) -> None:
        """Show all tagged bookmarks."""
        self.query_one(Bookmarks).has_tags_filter = (
            None if self.query_one(Bookmarks).has_tags_filter is True else True
        )

    def _search(self, search_text: str) -> None:
        """Handle a request to search for text in the bookmarks."""
        self.query_one(Bookmarks).text_filter = search_text

    def action_search(self) -> None:
        """Do some free-text searching."""
        self.app.push_screen(SearchInput(), callback=self._search)

    @on(ShowTaggedWith)
    def show_tagged_with(self, event: ShowTaggedWith) -> None:
        """Show all bookmarks tagged with a given tag.

        Args:
            event: The event that contains the tag to show.
        """
        self.query_one(Bookmarks).tag_filter = {event.tag}

    @on(ShowAlsoTaggedWith)
    def show_also_tagged_with(self, event: ShowAlsoTaggedWith) -> None:
        """Add a tag to any current tag filter and show the matching bookmarks.

        Args:
            event: The event that contains the tag to add.
        """
        self.query_one(Bookmarks).tag_filter |= {event.tag}

    @on(ClearTags)
    def clear_tags(self) -> None:
        """Clear any tags that are in use."""
        self.query_one(Bookmarks).tag_filter = set()

    async def post_result(self, result: BookmarkData | None) -> None:
        """Handle the result of an edit of a bookmark.

        Args:
            result: The result data, or `None` if the edit was cancelled.
        """
        if result:
            try:
                await self._api.add_bookmark(result)
                self.query_one(Bookmarks).update_bookmark(result).save()
                self.notify("Bookmark saved.")
            except API.Error as error:
                self.app.bell()
                self.notify(
                    str(error),
                    title="Error saving bookmark data",
                    severity="error",
                    timeout=10,
                )
                self.app.push_screen(
                    BookmarkInput(
                        self._api, result, known_tags=self.query_one(Bookmarks).all_tags
                    ),
                    callback=self.post_result,
                )
            except OSError as error:
                self.app.bell()
                self.notify(
                    f"Error saving the bookmarks.\n\n{error}",
                    title="Save Error",
                    severity="error",
                    timeout=8,
                )

    @on(CopyBookmarkURL)
    def copy_bookmark_to_clipboard(self) -> None:
        """Copy the currently-highlighted bookmark to the clipboard."""
        if (bookmark := self.query_one(Bookmarks).current_bookmark) is None:
            self.app.bell()
        elif bookmark.data.href:
            try:
                to_clipboard(bookmark.data.href)
            except PyperclipException:
                self.app.bell()
                self.notify(
                    "Clipboard support not available in your environment.",
                    severity="error",
                )
            else:
                self.notify("URL copied to the clipboard")

    @on(AddBookmark)
    def add(self) -> None:
        """Add a new bookmark."""
        self.app.push_screen(
            BookmarkInput(self._api, known_tags=self.query_one(Bookmarks).all_tags),
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
                    self._api,
                    bookmark.data,
                    known_tags=self.query_one(Bookmarks).all_tags,
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
            try:
                await self._api.delete_bookmark(bookmark.data.href)
            except API.Error:
                self.app.bell()
                self.notify(
                    "Error trying to delete the bookmark.",
                    title="Server Error",
                    severity="error",
                    timeout=8,
                )
                return
            try:
                self.query_one(Bookmarks).remove_bookmark(bookmark).save()
            except OSError as error:
                self.app.bell()
                self.notify(
                    f"Error saving the bookmarks.\n\n{error}",
                    title="Save Error",
                    severity="error",
                    timeout=8,
                )
                return
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
                    f"Are you sure you wish to delete this bookmark?\n\n[dim i]{bookmark.data.description}[/]",
                ),
                callback=partial(self._delete, bookmark),
            )

    @on(ToggleBookmarkRead)
    async def toggle_read(self) -> None:
        """Toggle the read/unread status of the current bookmark."""
        if (bookmark := self.query_one(Bookmarks).current_bookmark) is None:
            self.app.bell()
        else:
            bookmark.data.to_read = not bookmark.data.to_read
            await self.post_result(bookmark.data)

    @on(ToggleBookmarkPublic)
    async def toggle_public(self) -> None:
        """Toggle the public/private status of the current bookmark."""
        if (bookmark := self.query_one(Bookmarks).current_bookmark) is None:
            self.app.bell()
        else:
            bookmark.data.shared = not bookmark.data.shared
            await self.post_result(bookmark.data)


### main.py ends here
