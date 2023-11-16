"""Defines a widget for picking tags."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from typing_extensions import Self

##############################################################################
# Textual imports.
from textual import on
from textual.binding import Binding
from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option


##############################################################################
class Tags(OptionList):
    """A menu of tags."""

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

    def show(self, tags: list[str]) -> Self:
        """Show the given list of tags.

        Args:
            tags: The tags to show in the widget.

        Returns:
            Self.
        """
        self.can_focus = bool(tags)
        return self.clear_options().add_options([Option(tag, id=tag) for tag in tags])

    @dataclass
    class TagMessage(Message):
        """Base class for the tag messages."""

        tag: str
        """The tag associated with the message."""

    class ShowTaggedWith(TagMessage):
        """Message to say bookmarks of this tag should be shown."""

    class ShowAlsoTaggedWith(TagMessage):
        """Message to say bookmarks also of this tag should be shown."""

    def _on_focus(self) -> None:
        """Highlight the first item on focus, if none highlighted."""
        if self.option_count and self.highlighted is None:
            self.highlighted = 0

    @on(OptionList.OptionSelected)
    def show_tagged(self, event: OptionList.OptionSelected) -> None:
        """Request that bookmarks of a given tag are shown.

        Args:
            event: The event to handle.
        """
        if event.option.id is not None:
            self.post_message(self.ShowTaggedWith(event.option.id))

    def action_also_tagged(self) -> None:
        """Request that the current tag is added to any tag filter in place."""
        if self.highlighted is not None:
            if (tag := self.get_option_at_index(self.highlighted).id) is not None:
                self.post_message(self.ShowAlsoTaggedWith(tag))


### tags.py ends here
