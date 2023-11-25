"""A dialog that lets the user provide a token."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from webbrowser import open as open_url

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input


##############################################################################
class TokenInput(ModalScreen[str | None]):
    """A modal screen that lets the user enter an API token."""

    DEFAULT_CSS = """
    TokenInput {
        align: center middle;
    }

    TokenInput Vertical {
        padding: 1 2;
        width: 40%;
        min-width: 70;
        height: auto;
        background: $surface;
        border: panel $error;
        border-title-color: $text;
    }

    TokenInput Label {
        width: 1fr;
        height: auto;
        padding-left: 1;
        padding-right: 1;
        margin-bottom: 1;
    }

    TokenInput > Vertical > Horizontal {
        margin-top: 1;
        height: auto;
        align-horizontal: right;
    }

    TokenInput > Vertical > Horizontal > Horizontal {
        margin-left: 1;
        height: auto;
    }

    TokenInput Button {
        margin-right: 1;
    }
    """

    BINDINGS = [("escape", "cancel"), ("f1", "get_token")]

    def compose(self) -> ComposeResult:
        """Compose the content of the screen."""
        with Vertical() as dialog:
            dialog.border_title = "API Token Required"
            yield Label(
                "To use the [i]pinboard.in[/] API you will need an API token. "
                "You can [@click=screen.get_token]get your API token from your "
                "account page on [i]pinboard.in[/][/]."
            )
            yield Input(placeholder="Paste the token here")
            with Horizontal():
                with Horizontal():
                    yield Button("Go to token [dim]\\[F1][/]", id="get-token")
                yield Button("Connect", id="connect", variant="primary")
                yield Button("Cancel [dim]\\[Esc][/]", id="cancel", variant="error")

    @on(Button.Pressed, "#connect")
    @on(Input.Submitted)
    def confirm(self) -> None:
        """React to the user confirming their input."""
        if token := self.query_one(Input).value.strip():
            self.dismiss(token)
        else:
            self.notify("Please provide a token", severity="error")

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        """React to the user cancelling the dialog."""
        self.dismiss(None)

    @on(Button.Pressed, "#get-token")
    def action_get_token(self) -> None:
        """Open the page for getting an API token."""
        open_url("https://pinboard.in/settings/password")
        self.query_one(Input).focus()


### token_input.py ends here
