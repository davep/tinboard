"""Defines the main filter menu for the application."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from typing_extensions import Final

##############################################################################
# Textual imports.
from textual import on
from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option

##############################################################################
# Rich imports.
from rich.table import Table


##############################################################################
class Filters(OptionList):
    """The main menu for the application."""

    DEFAULT_CSS = """
    Filters {
        height: auto;
        border: blank;
    }

    Filters:focus {
        border: blank;
    }

    Filters > .option-list--option {
        padding: 0 1;
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

    @classmethod
    def shortcut(cls, option: str) -> str:
        """Get the shortcut for a given filter menu option.

        Args:
            option: The option to get the shortcut for.

        Returns:
            The shortcut for the option.
        """
        return cls.OPTIONS[option]

    @classmethod
    def _prompt(cls, name: str) -> Table:
        """Create a prompt for a filter.

        Args:
            name: The name of the filter.

        Returns:
            A renderable to use in the menu display.
        """
        prompt = Table.grid(expand=True)
        prompt.add_column(no_wrap=True, ratio=1)
        prompt.add_column(no_wrap=True, justify="left")
        prompt.add_row(name, f"[dim]\\[{cls.shortcut(name)}][/]")
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
            *[
                Option(self._prompt(option), id=option.lower())
                for option in self.OPTIONS
            ],
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

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

    @dataclass
    class ShowTaggedWith(Message):
        """Filter with the given tag."""

        tag: str
        """The tag to filter on."""

    @classmethod
    def core_filter_message(cls, name: str) -> CoreFilter:
        """Get a core filter message based off its name.

        Args:
            name: The name of the filter.

        Returns:
            A message to request that filter be used.
        """
        return {
            "all": cls.ShowAll,
            "unread": cls.ShowUnread,
            "read": cls.ShowRead,
            "public": cls.ShowPublic,
            "private": cls.ShowPrivate,
            "tagged": cls.ShowTagged,
            "untagged": cls.ShowUntagged,
        }[name.lower()]()

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        """Handle a menu option selection.

        Args:
            event: The event to handle.
        """
        event.stop()
        assert event.option.id is not None
        self.post_message(self.core_filter_message(event.option.id))


### menu.py ends here
