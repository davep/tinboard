"""Defines the main menu for the application."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from typing import cast
from typing_extensions import Final

##############################################################################
# Textual imports.
from textual import on
from textual.binding import Binding
from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option, Separator

##############################################################################
# Rich imports.
from rich.table import Table

##############################################################################
# Local imports.
from .bookmarks import Bookmark, Bookmarks


##############################################################################
class Menu(OptionList):
    """The main menu for the application."""

    DEFAULT_CSS = """
    Menu {
        scrollbar-gutter: stable;
    }

    Menu > .option-list--option {
        padding: 0 1;
    }
    """

    _CORE_OPTIONS: Final[dict[str, str]] = {
        "All": "a",
        "Unread": "R",
        "Read": "r",
        "Private": "P",
        "Public": "p",
        "Untagged": "T",
        "Tagged": "t",
    }
    """The core options of the menu."""

    _CORE_PREFIX: Final[str] = "core-"
    """The prefix given to each core filter option."""

    _TAG_PREFIX: Final[str] = "tag-"
    """The prefix given to each tag filter option."""

    BINDINGS = [Binding("+", "also_tagged")]

    @classmethod
    def shortcut(cls, option: str) -> str:
        """Get the shortcut for a given filter menu option.

        Args:
            option: The option to get the shortcut for.

        Returns:
            The shortcut for the option.
        """
        return cls._CORE_OPTIONS[option]

    @classmethod
    def _main_filter_prompt(cls, name: str) -> Table:
        """Create a prompt for a main filter.

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

    @classmethod
    def _tag_filter_prompt(cls, tag: str) -> Table:
        """Create a prompt for a tag filter.

        Args:
            tag: The tag to filter with.

        Returns:
            A renderable to use in the menu display.
        """
        prompt = Table.grid(expand=True)
        prompt.add_column(no_wrap=True, ratio=1)
        prompt.add_column(no_wrap=True, justify="left")
        prompt.add_row(tag, "[dim]\\[+][/]")
        return prompt

    def refresh_options(self, bookmarks: Bookmarks | None = None) -> None:
        """Refresh the options in the menu.

        Args:
            bookmarks: The bookmarks to take data from.
        """
        options: list[Option | Separator] = [
            Option(
                self._main_filter_prompt(prompt),
                id=f"{self._CORE_PREFIX}{prompt.lower()}",
            )
            for prompt in self._CORE_OPTIONS
        ]
        if bookmarks:
            if tags := bookmarks.tags:
                options.append(Separator())
                options.extend(
                    Option(self._tag_filter_prompt(tag), id=f"{self._TAG_PREFIX}{tag}")
                    for tag in tags
                )
        self.clear_options().add_options(options)
        self.highlighted = 0

    def on_mount(self) -> None:
        """Initialise the menu once the DOM is ready."""
        self.refresh_options()

    @classmethod
    def is_core_filter(cls, option: Option) -> bool:
        """Is the given option a core filter?

        Args:
            option: The option to check.

        Returns:
            `True` if it's a core filter option, `False` if not.
        """
        return option.id is not None and option.id.startswith(cls._CORE_PREFIX)

    @classmethod
    def is_tag_filter(cls, option: Option) -> bool:
        """Is the given option a tag filter?

        Args:
            option: The option to check.

        Returns:
            `True` if it's a tag filter option, `False` if not.
        """
        return option.id is not None and option.id.startswith(cls._TAG_PREFIX)

    @staticmethod
    def filter_value(prefix: str, option: Option) -> str:
        """Get the filtering value for the given option.

        Args:
            prefix: The prefix for the filter option type.
            option: The option to get the value from.

        Returns:
            The value to filter with.
        """
        assert option.id is not None
        *_, value = option.id.partition(prefix)
        return value

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

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        """Handle a menu option selection.

        Args:
            event: The event to handle.
        """
        event.stop()
        if self.is_core_filter(event.option):
            self.post_message(
                {
                    "all": self.ShowAll,
                    "unread": self.ShowUnread,
                    "read": self.ShowRead,
                    "public": self.ShowPublic,
                    "private": self.ShowPrivate,
                    "tagged": self.ShowTagged,
                    "untagged": self.ShowUntagged,
                }[self.filter_value(self._CORE_PREFIX, event.option)]()
            )
        elif self.is_tag_filter(event.option):
            self.post_message(
                self.ShowTaggedWith(self.filter_value(self._TAG_PREFIX, event.option))
            )

    @dataclass
    class ShowAlsoTaggedWith(Message):
        """Add a tag to the current tag filter."""

        tag: str
        """The tag to add."""

    def action_also_tagged(self) -> None:
        """Add the highlighted tag to the current tag filter."""
        if self.highlighted is not None:
            if self.is_tag_filter(
                option := cast(Bookmark, self.get_option_at_index(self.highlighted))
            ):
                self.post_message(
                    self.ShowAlsoTaggedWith(self.filter_value(self._TAG_PREFIX, option))
                )


### menu.py ends here
