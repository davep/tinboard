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
from .data import load_configuration, save_configuration, token_file, ExitStates


##############################################################################
class Tinboard(App[ExitStates]):
    """The application."""

    BINDINGS = [
        Binding("ctrl+backslash", "gndn"),
        Binding("ctrl+p", "command_palette", priority=True),
    ]

    def __init__(self) -> None:
        """Initialise the application."""
        super().__init__()
        self.dark = load_configuration().dark_mode

    def token_bounce(self, token: str | None) -> None:
        """Handle the result of asking the user for their API token.

        Args:
            token: The resulting token.
        """
        if token:
            token_file().write_text(token, encoding="utf-8")
            self.push_screen(Main(token))
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

    def _watch_dark(self) -> None:
        """Save the light/dark mode configuration choice."""
        configuration = load_configuration()
        configuration.dark_mode = self.dark
        save_configuration(configuration)


### app.py ends here
