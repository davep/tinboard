"""Provides a TextArea that's easier to use."""

##############################################################################
# Textual imports.
from textual.events import Key
from textual.widgets import TextArea as BaseTextArea


##############################################################################
class TextArea(BaseTextArea):
    """A Textual TextArea with some QOL tweaks."""

    DEFAULT_CSS = """
    TextArea {
        background: $boost;
        color: $text;
        padding: 0 2;
        border: tall $background;

        &:focus {
            border: tall $accent;
        }
    }
    """

    def _retheme(self) -> None:
        """Swap between a dark and light theme when the mode changes."""
        self.theme = "vscode_dark" if self.app.dark else "github_light"

    def on_mount(self) -> None:
        """Configure the text area on mount."""
        self.show_line_numbers = False
        self.watch(self.app, "dark", self._retheme)

    async def _on_key(self, event: Key) -> None:
        """Allow tab to move along the focus chain."""
        if event.key == "tab":
            event.prevent_default()
            self.screen.focus_next()


### text_area.py ends here
