"""Provides a settings screen."""

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox

##############################################################################
# Local imports.
from ..data import load_configuration, save_configuration


##############################################################################
class Settings(ModalScreen[None]):
    """A modal dialog for editing settings."""

    CSS = """
    Settings {
        align: center middle;

        &> Vertical {
            height: auto;
            width: auto;
            background: $surface;
            border: panel $primary;
            border-title-color: $accent;
            padding-top: 1;
        }

        #buttons {
            height: auto;
            width: 100%;
            margin-top: 1;
            align-horizontal: right;
        }

        Checkbox {
            min-width: 1fr;
        }

        Button {
            margin-right: 1;
        }
    }
    """

    BINDINGS = [("escape", "cancel"), ("f2", "save")]

    def compose(self) -> ComposeResult:
        """Compose the layout of the dialog."""
        with Vertical() as dialog:
            dialog.border_title = "Application Settings"
            config = load_configuration()
            yield Checkbox(
                "Bookmarks are private by default", config.default_private, id="private"
            )
            yield Checkbox(
                "Bookmarks are read-later by default",
                config.default_read_later,
                id="read-later",
            )
            with Horizontal(id="buttons"):
                yield Button("Save [dim]\\[F2][/]", id="save")
                yield Button("Cancel [dim]\\[Esc][/]", id="cancel")

    @on(Button.Pressed, "#save")
    def action_save(self) -> None:
        """Save the configuration."""
        config = load_configuration()
        config.default_private = self.query_one("#private", Checkbox).value
        config.default_read_later = self.query_one("#read-later", Checkbox).value
        save_configuration(config)
        self.dismiss(None)

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        """Cancel the edit of the bookmark data."""
        self.dismiss(None)


### settings.py ends here
