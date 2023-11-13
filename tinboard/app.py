"""The main application class."""

##############################################################################
# Textual imports.
from textual.app import App

##############################################################################
# Local imports.
from .screens import Main


##############################################################################
class TinBoard(App[None]):
    """The application."""

    def on_mount(self) -> None:
        """Display the main screen."""
        self.push_screen(Main())


### app.py ends here
