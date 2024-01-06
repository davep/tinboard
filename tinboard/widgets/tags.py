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
from textual.reactive import var
from textual.widgets.option_list import Option, OptionDoesNotExist

##############################################################################
# Rich imports.
from rich.console import RenderableType
from rich.emoji import Emoji
from rich.table import Table

##############################################################################
# Local imports.
from ..messages import ClearTags, ShowAlsoTaggedWith, ShowTaggedWith
from .extended_option_list import OptionListEx


##############################################################################
class Tags(OptionListEx):
    """A menu of tags."""

    CONTEXT_HELP = """
    ## Tag list keys

    The following keys are available in the list of tags:

    | Key | Description |
    | - | - |
    | <kbd>Enter</kbd> | Show bookmarks with this tag in the bookmark list. |
    | <kbd>+</kbd> | Add this tag to any tag filter active in the bookmark list. |
    """

    DEFAULT_CSS = """
    Tags {
        &:focus {
            border: blank;
        }

        &> .option-list--option {
            padding: 0 1;
        }
    }
    """

    BINDINGS = [
        Binding("enter", "select", "Show tagged", show=True),
        Binding("+", "also_tagged", "Show also tagged"),
    ]

    def _prompt(self, tag: str, count: int) -> RenderableType:
        """A prompt for the given tag.

        Args:
            tag: The tag to build a prompt for.
            count: The count for that tag.

        Returns:
            The prompt for the tag.
        """
        prompt = Table.grid(expand=True)
        prompt.add_column(ratio=1)
        prompt.add_column(justify="right")
        prompt.add_row(tag, f"[dim i]{count}[/]")
        return prompt

    def _sorted(self, tags: list[tuple[str, int]]) -> list[tuple[str, int]]:
        """Sort the tags.

        Args:
            tags: The tags to sort.

        Returns:
            The tags in the desired sort order.
        """
        return tags

    def show(self, tags: list[tuple[str, int]]) -> Self:
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
                [
                    Option(self._prompt(tag, count), id=tag)
                    for tag, count in self._sorted(tags)
                ]
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
    def _show_tagged(self, event: OptionListEx.OptionSelected) -> None:
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


##############################################################################
class TagsMenu(Tags):
    """A version of `Tags` to use as part of the main menu."""

    CONTEXT_HELP = f"{Tags.CONTEXT_HELP}| <kbd>c</kbd> | Clear any active tag filter. |"

    BINDINGS = [Binding("c", "clear", "Clear Tags")]

    sort_by_count: var[bool] = var(False)
    """Should the tags be sorted by count?"""

    def _sorted(self, tags: list[tuple[str, int]]) -> list[tuple[str, int]]:
        """Sort the tags.

        Args:
            tags: The tags to sort.

        Returns:
            The tags in the desired sort order.
        """
        return (
            sorted(tags, key=lambda tag: tag[1], reverse=True)
            if self.sort_by_count
            else tags
        )

    def action_clear(self) -> None:
        """Clear any active tags."""
        self.post_message(ClearTags())


##############################################################################
class InlineTags(Tags):
    """A version of the `Tags` widget intended to embed in another."""

    DEFAULT_CSS = """
    InlineTags > .option-list--option {
        padding: 0;
    }
    """

    _ICON: Final[str] = Emoji.replace(":bookmark: ")
    """The icon to show before tags."""

    def _prompt(self, tag: str, count: int) -> RenderableType:
        """A prompt for the given tag.

        Args:
            The tag to build a prompt for.

        Returns:
            The prompt for the tag.
        """
        del count
        return f"{self._ICON} {tag}"


### tags.py ends here
