"""Provides a dialog for editing bookmark details."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Label

##############################################################################
# Pinboard API imports.
from aiopinboard.bookmark import Bookmark as BookmarkData

##############################################################################
# Local imports.
from ..widgets import TextArea


##############################################################################
class BookmarkInput(ModalScreen[BookmarkData | None]):
    DEFAULT_CSS = """
    BookmarkInput {
        align: center middle;
    }

    BookmarkInput > Vertical {
        width: 60%;
        height: auto;
        background: $surface;
        border: panel $primary;
        border-title-color: $accent;
    }

    BookmarkInput #description {
        height: 10;
    }

    BookmarkInput > Vertical > Horizontal {
        height: auto;
    }

    BookmarkInput #buttons {
        margin-top: 1;
        align-horizontal: right;
    }

    BookmarkInput Button {
        margin-right: 1;
    }

    BookmarkInput Label {
        margin: 1 0 0 1;
    }

    BookmarkInput #flags {
        margin-top: 1;
    }
    """

    BINDINGS = [Binding("escape", "cancel")]

    def __init__(self, bookmark: BookmarkData | None = None) -> None:
        """Initialise the bookmark input dialog.

        Args:
            bookmark: The bookmark to edit, or `None` for a new one.
        """
        super().__init__()
        self._bookmark = bookmark

    def compose(self) -> ComposeResult:
        """Compose the layout of the dialog."""
        with Vertical() as dialog:
            dialog.border_title = "Bookmark"
            yield Label("URL:")
            yield Input(placeholder="Bookmark URL", id="url")
            yield Label("Title:")
            yield Input(placeholder="Bookmark title", id="title")
            yield Label("Description:")
            yield TextArea(id="description")
            yield Label("Tags:")
            yield Input(placeholder="Bookmark tags (space separated)", id="tags")
            with Horizontal(id="flags"):
                yield Checkbox("Private", id="private")
                yield Checkbox("Read Later", id="read-later")
            with Horizontal(id="buttons"):
                yield Button("Save", id="save")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        """Configure the dialog once it's in the DOM."""
        if self._bookmark:
            self.query_one("#url", Input).value = self._bookmark.href
            self.query_one("#title", Input).value = self._bookmark.title
            self.query_one("#description", TextArea).text = self._bookmark.description
            self.query_one("#tags", Input).value = " ".join(self._bookmark.tags)
            self.query_one("#private", Checkbox).value = not self._bookmark.shared
            self.query_one("#read-later", Checkbox).value = self._bookmark.unread

    @on(Button.Pressed, "#save")
    def save(self) -> None:
        """Save the bookmark data."""
        self.dismiss(None)

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        """Cancel the edit of the bookmark data."""
        self.dismiss(None)


### bookmark_input.py ends here
