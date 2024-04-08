"""The main application class."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
import os

##############################################################################
# Textual imports.
from textual.app import App
from textual.binding import Binding

##############################################################################
# Local imports.
from .data import (
    Bookmarks,
    ExitStates,
    load_configuration,
    save_configuration,
    token_file,
)
from .pinboard import API, BookmarkData
from .screens import BookmarkInput, Main, TokenInput
from .widgets.filters import Filters


##############################################################################
class Tinboard(App[ExitStates]):
    """The application."""

    BINDINGS = [
        Binding("ctrl+backslash", "gndn"),
        Binding("ctrl+p", "command_palette", priority=True),
    ]

    def __init__(self, initial_filter: str | None = None) -> None:
        """Initialise the application.

        Args:
            initial_filter: The initial filter to apply when starting up.
        """
        super().__init__()
        self.dark = load_configuration().dark_mode
        self._initial_filter: set[type[Filters.CoreFilter]] = (
            set()
            if initial_filter is None
            else {Filters.core_filter_type(initial_filter)}
        )
        """The initial filter to apply when showing the main screen."""

    def token_bounce(self, token: str | None) -> None:
        """Handle the result of asking the user for their API token.

        Args:
            token: The resulting token.
        """
        if token:
            token_file().write_text(token, encoding="utf-8")
            self.push_screen(Main(API(token), self._initial_filter))
        else:
            self.exit(ExitStates.TOKEN_NEEDED)

    @staticmethod
    def environmental_token() -> str | None:
        """Try and get an API token from the environment.

        Returns:
           An API token found in the environment, or `None` if one wasn't found.
        """
        return os.environ.get("TINBOARD_API_TOKEN")

    @property
    def api_token(self) -> str | None:
        """The API token for talking to Pinboard.

        If the token is found in the environment, it will be used. If not a
        saved token will be looked for and used. If one doesn't exist the
        value will be `None`.
        """
        try:
            return self.environmental_token() or token_file().read_text(
                encoding="utf-8"
            )
        except IOError:
            pass
        return None

    async def inline_add(self, result: BookmarkData | None = None) -> None:
        """Handle the result adding a bookmark inline.

        Args:
            result: The result data, or `None` if the entry was cancelled.
        """
        if result:
            try:
                if token := self.api_token:
                    await API(token).add_bookmark(result)
            except API.Error:
                self.exit(ExitStates.INLINE_SAVE_ERROR)
        self.exit()

    def on_mount(self) -> None:
        """Display the main screen.

        Note:
            If the Pinboard API token isn't known, the token input dialog
            will first be shown; the main screen will then only be shown
            once the token has been acquired.
        """
        if token := self.api_token:
            if self.is_inline:
                # If we're running as an inline application, that means we
                # should simply be showing the bookmark input screen for
                # quick input. Note disabling the command palette too, which
                # has problems with inline mode.
                self.use_command_palette = False
                self.push_screen(
                    BookmarkInput(API(token), known_tags=Bookmarks().load().tags),
                    callback=self.inline_add,
                )
            else:
                # We're not in inline mode so we'll show the normal
                # application screen.
                self.push_screen(Main(API(token), self._initial_filter))
        else:
            self.push_screen(TokenInput(), callback=self.token_bounce)

    def _watch_dark(self) -> None:
        """Save the light/dark mode configuration choice."""
        configuration = load_configuration()
        configuration.dark_mode = self.dark
        save_configuration(configuration)


### app.py ends here
