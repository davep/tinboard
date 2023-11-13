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

##############################################################################
# Local imports.
from .screens import Main, TokenInput


##############################################################################
class TinBoard(App[None]):
    """The application."""

    def token_bounce(self, token: str | None) -> None:
        """Handle the result of asking the user for their API token.

        Args:
            token: The resulting token.
        """
        if token:
            self.push_screen(Main(token))
        else:
            self.exit()

    def on_mount(self) -> None:
        """Display the main screen."""
        if token := os.environ.get("TINBOARD_API_TOKEN"):
            self.push_screen(Main(token))
        else:
            self.push_screen(TokenInput(), callback=self.token_bounce)


### app.py ends here
