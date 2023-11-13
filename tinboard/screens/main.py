"""The main screen for the application."""

##############################################################################
# Textual imports.
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header


##############################################################################
class Main(Screen):
    """The main application screen."""

    TITLE = "TinBoard"
    SUB_TITLE = "A pinboard.in client"

    def compose(self) -> ComposeResult:
        """Lay out the content of the screen."""
        yield Header()
        yield Footer()


### main.py ends here
