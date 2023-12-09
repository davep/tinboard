"""Defines a widget for picking tags."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from typing_extensions import Final, Self

##############################################################################
# Textual imports.
from textual import on
from textual.binding import Binding
from textual.events import Focus
from textual.widgets.option_list import Option, OptionDoesNotExist

##############################################################################
# Rich imports.
from rich.emoji import Emoji

##############################################################################
# Local imports.
from ..messages import ShowAlsoTaggedWith, ShowTaggedWith
from .extended_option_list import OptionListEx


##############################################################################
ICON: Final[str] = Emoji.replace(":bookmark: ")
"""The icon to show before tags."""


##############################################################################
class Tags(OptionListEx):
    """A menu of tags."""

    CONTEXT_HELP = """\
    ## Tag list keys

    The following keys are available in the list of tags:

    | Key | Description |
    | - | - |
    | <kbd>Enter</kbd> | Show bookmarks with this tag in the bookmark list. |
    | <kbd>+</kbd> | Add this tag to any tag filter active in the bookmark list. |
    """

    DEFAULT_CSS = """
    Tags, Tags:focus {
        border: blank;
    }

    Tags > .option-list--option {
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("enter", "select", "Show tagged", show=True),
        Binding("+", "also_tagged", "Show also tagged"),
    ]

    def show(self, tags: list[str], with_icon: bool = False) -> Self:
        """Show the given list of tags.

        Args:
            tags: The tags to show in the widget.

        Returns:
            Self.
        """
        self.can_focus = bool(tags)
        highlighted_tag = (
            self.get_option_at_index(self.highlighted).id
            if self.highlighted is not None
            else None
        )
        try:
            return self.clear_options().add_options(
                [Option(f"{ICON if with_icon else ''}{tag}", id=tag) for tag in tags]
            )
        finally:
            if tags:
                try:
                    self.highlighted = self.get_option_index(highlighted_tag or "")
                except OptionDoesNotExist:
                    self.highlighted = 0

    def _on_focus(self, _: Focus) -> None:
        """Highlight the first item on focus, if none highlighted."""
        if self.option_count and self.highlighted is None:
            self.highlighted = 0

    @on(OptionListEx.OptionSelected)
    def show_tagged(self, event: OptionListEx.OptionSelected) -> None:
        """Request that bookmarks of a given tag are shown.

        Args:
            event: The event to handle.
        """
        if event.option.id is not None:
            self.post_message(ShowTaggedWith(event.option.id))

    def action_also_tagged(self) -> None:
        """Request that the current tag is added to any tag filter in place."""
        if self.highlighted is not None:
            if (tag := self.get_option_at_index(self.highlighted).id) is not None:
                self.post_message(ShowAlsoTaggedWith(tag))


### tags.py ends here
