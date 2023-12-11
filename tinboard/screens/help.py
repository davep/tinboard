"""The help screen of the application."""

##############################################################################
# Python imports.
from inspect import cleandoc
from typing import Any
from webbrowser import open as open_url

##############################################################################
# Textual imports.
from textual import (  # pylint:disable=no-name-in-module
    on,
    __version__ as textual_version,
)
from textual.app import ComposeResult
from textual.containers import Center, Vertical, VerticalScroll
from textual.screen import ModalScreen, Screen
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

{{context_help}}

## Other

Tinboard was created by and is maintained by [Dave Pearson](https://www.davep.org/).


Tinboard is Free Software and can be [found on GitHub](https://github.com/davep/tinboard).


This version of Tinboard is using [Textual](https://textual.textualize.io/) v{textual_version}.
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

    Help VerticalScroll {
        scrollbar-gutter: stable;
    }

    Help Center {
        height: auto;
        width: 100%;
        border-top: solid $primary;
        padding-top: 1;
    }
    """

    BINDINGS = [("escape", "close")]

    def __init__(self, help_for: Screen[Any]) -> None:
        """Initialise the help screen.

        Args:
            help_for: The screen to show the help for.
        """
        super().__init__()
        self._context_help = "\n\n".join(
            cleandoc(getattr(helper, "CONTEXT_HELP"))
            for helper in reversed(
                (
                    help_for.focused if help_for.focused is not None else help_for
                ).ancestors_with_self
            )
            if hasattr(helper, "CONTEXT_HELP")
        ).strip()

    def compose(self) -> ComposeResult:
        """Compose the layout of the help screen."""
        with Vertical() as help_screen:
            help_screen.border_title = "Help"
            with VerticalScroll():
                yield Markdown(HELP.format(context_help=self._context_help))
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
