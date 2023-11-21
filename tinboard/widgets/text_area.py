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
    }

    TextArea:focus {
        border: tall $accent;
    }
    """

    def on_mount(self) -> None:
        """Configure the text area on mount."""
        self.show_line_numbers = False

    async def _on_key(self, event: Key) -> None:
        """Allow tab to move along the focus chain."""
        if event.key == "tab":
            event.prevent_default()
            self.screen.focus_next()


### text_area.py ends here
