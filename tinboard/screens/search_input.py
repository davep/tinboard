"""A dialog for getting text to search for."""

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input


##############################################################################
class SearchInput(ModalScreen[str]):
    """A modal screen to get search text from the user."""

    DEFAULT_CSS = """
    SearchInput {
        align: center middle;
    }

    SearchInput Vertical {
        border: round $accent;
        width: 60%;
        height: auto;
        background: $surface;
    }

    SearchInput Input, SearchInput Input:focus {
        margin: 0;
        padding: 1;
        border: none;
        background: $surface;
    }
    """

    BINDINGS = [("escape", "escape")]

    def compose(self) -> ComposeResult:
        """Compose the input dialog."""
        with Vertical():
            yield Input(
                placeholder="Case-insensitive text to look for in the bookmarks"
            )

    @on(Input.Submitted)
    def search(self) -> None:
        """Perform the search."""
        self.dismiss(self.query_one(Input).value.strip())

    def action_escape(self) -> None:
        """Escape out without searching."""
        self.app.pop_screen()


### search_input.py ends here
