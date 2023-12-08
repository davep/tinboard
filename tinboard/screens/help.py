"""The help screen of the application."""

##############################################################################
# Python imports.
from webbrowser import open as open_url

##############################################################################
# Textual imports.
from textual import on, __version__ as textual_version
from textual.app import ComposeResult
from textual.containers import Center, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown

##############################################################################
# Local imports.
from .. import __version__

##############################################################################
# The help text.
HELP = f"""\
# Tinboard v{__version__}

## Introduction

`Tinboard` is a terminal-based client for [pinboard.in](https://pinboard.in/).

## TODO

More help will appear here. This is just about getting the screen in place.

## Other

This version if Tinboard is using [Textual](https://textual.textualize.io/) v{textual_version}.
"""


##############################################################################
class Help(ModalScreen[None]):
    """The help screen."""

    DEFAULT_CSS = """
    Help {
        align: center middle;
    }

    Help Vertical {
        width: 75%;
        height: 90%;
        background: $surface;
        border: panel $primary;
        border-title-color: $accent;
    }

    Help Markdown {
        height: 1fr;
    }

    Help Center {
        height: auto;
        width: 100%;
        border-top: solid $primary;
        padding-top: 1;
    }
    """

    BINDINGS = [("escape", "close")]

    def compose(self) -> ComposeResult:
        """Compose the layout of the help screen."""
        with Vertical() as help_screen:
            help_screen.border_title = "Help"
            with VerticalScroll():
                yield Markdown(HELP)
            with Center():
                yield Button("Okay [dim]\\[Esc]")

    @on(Button.Pressed)
    def action_close(self) -> None:
        """Close the help screen."""
        self.dismiss(None)

    @on(Markdown.LinkClicked)
    def visit(self, event: Markdown.LinkClicked) -> None:
        """Visit any link clicked in the help."""
        open_url(event.href)


### help.py ends here
