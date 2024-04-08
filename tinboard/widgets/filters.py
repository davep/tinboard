"""Defines the main filter menu for the application."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from typing import Final

##############################################################################
# Rich imports.
from rich.table import Table

##############################################################################
# Textual imports.
from textual import on
from textual.message import Message
from textual.reactive import var
from textual.widgets.option_list import Option

##############################################################################
# Local imports.
from ..data import Bookmarks
from .extended_option_list import OptionListEx


##############################################################################
class Filters(OptionListEx):
    """The main menu for the application."""

    DEFAULT_CSS = """
    Filters {
        height: auto;
        border: blank;

        .option-list--option {
            padding: 0 1;
        }

        &:focus {
            border: blank;
        }
    }
    """

    OPTIONS: Final[dict[str, str]] = {
        "All": "a",
        "Unread": "R",
        "Read": "r",
        "Private": "P",
        "Public": "p",
        "Untagged": "T",
        "Tagged": "t",
    }
    """The core options of the menu."""

    counts: var[Bookmarks.Counts] = var(Bookmarks.Counts(), init=False)
    """Holds the counts for the bookmarks."""

    @classmethod
    def shortcut(cls, option: str) -> str:
        """Get the shortcut for a given filter menu option.

        Args:
            option: The option to get the shortcut for.

        Returns:
            The shortcut for the option.
        """
        return cls.OPTIONS[option]

    def _prompt(self, name: str) -> Table:
        """Create a prompt for a filter.

        Args:
            name: The name of the filter.

        Returns:
            A renderable to use in the menu display.
        """
        prompt = Table.grid(expand=True)
        prompt.add_column(no_wrap=True, ratio=1)
        prompt.add_column(no_wrap=True, justify="left")
        prompt.add_column(no_wrap=True, justify="left")
        prompt.add_row(
            name,
            f"[dim i]{getattr(self.counts, name.lower())}[/]",
            f"  [dim]\\[{self.shortcut(name)}][/]",
        )
        return prompt

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,  # pylint:disable=redefined-builtin
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Initialise the filter menu.

        Args:
            name: The name of the widget description.
            id: The ID of the widget description in the DOM.
            classes: The CSS classes of the widget description.
            disabled: Whether the widget description is disabled or not.
        """
        super().__init__(
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self.add_options(
            [Option(self._prompt(option), id=option.lower()) for option in self.OPTIONS]
        )

    def on_focus(self) -> None:
        """Try and ensure an option is highlighted when we get focus."""
        if self.highlighted is None and self.option_count:
            self.highlighted = 0

    class CoreFilter(Message):
        """Base class for the core filters."""

    class ShowAll(CoreFilter):
        """Show all bookmarks."""

    class ShowUnread(CoreFilter):
        """Show unread bookmarks."""

    class ShowRead(CoreFilter):
        """Show read bookmarks"""

    class ShowPublic(CoreFilter):
        """Show the bookmarks that are public."""

    class ShowPrivate(CoreFilter):
        """Show the bookmarks that are private."""

    class ShowTagged(CoreFilter):
        """Show the bookmarks that have tags."""

    class ShowUntagged(CoreFilter):
        """Show the bookmarks that have no tags."""

    _CORE_FILTERS: Final[dict[str, type[CoreFilter]]] = {
        "all": ShowAll,
        "unread": ShowUnread,
        "read": ShowRead,
        "public": ShowPublic,
        "private": ShowPrivate,
        "tagged": ShowTagged,
        "untagged": ShowUntagged,
    }
    """The core filters and their message mappings."""

    @classmethod
    def core_filter_names(cls) -> list[str]:
        """The names for the core filters.

        Return:
            The names of the core filters.
        """
        return list(cls._CORE_FILTERS)

    @classmethod
    def core_filter_type(cls, name: str) -> type[CoreFilter]:
        """Get a core filter message type based off its name.

        Args:
            name: The name of the filter.

        Returns:
            A message type to request that filter be used.
        """
        return cls._CORE_FILTERS[name.lower()]

    @classmethod
    def core_filter_message(cls, name: str) -> CoreFilter:
        """Get a core filter message based off its name.

        Args:
            name: The name of the filter.

        Returns:
            A message to request that filter be used.
        """
        return cls.core_filter_type(name)()

    @on(OptionListEx.OptionSelected)
    def handle_selection(self, event: OptionListEx.OptionSelected) -> None:
        """Handle a menu option selection.

        Args:
            event: The event to handle.
        """
        event.stop()
        assert event.option.id is not None
        self.post_message(self.core_filter_message(event.option.id))

    def _watch_counts(self) -> None:
        """React to the counts being changed."""
        for filter_name in self.OPTIONS:
            self.replace_option_prompt(filter_name.lower(), self._prompt(filter_name))


### menu.py ends here
