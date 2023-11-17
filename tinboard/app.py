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
from .screens import Main, TokenInput
from .utils import token_file


##############################################################################
class TinBoard(App[None]):
    """The application."""

    BINDINGS = [
        Binding("ctrl+backslash", "gndn"),
        Binding("ctrl+p", "command_palette", "Commands", priority=True),
    ]

    def token_bounce(self, token: str | None) -> None:
        """Handle the result of asking the user for their API token.

        Args:
            token: The resulting token.
        """
        if token:
            token_file().write_text(token, encoding="utf-8")
            self.push_screen(Main(token))
        else:
            self.exit()

    @property
    def api_token(self) -> str | None:
        """The API token for talking to Pinboard.

        If the token is found in the environment, it will be used. If not a
        saved token will be looked for and used. If one doesn't exist the
        value will be `None`.
        """
        if token := os.environ.get("TINBOARD_API_TOKEN"):
            return token
        try:
            if token_file().exists() and (
                token := token_file().read_text(encoding="utf-8")
            ):
                return token
        except IOError:
            pass
        return None

    def on_mount(self) -> None:
        """Display the main screen.

        Note:
            If the Pinboard API token isn't known, the token input dialog
            will first be shown; the main screen will then only be shown
            once the token has been acquired.
        """
        if token := self.api_token:
            self.push_screen(Main(token))
        else:
            self.push_screen(TokenInput(), callback=self.token_bounce)


### app.py ends here
