"""Defines the main menu for the application."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Textual imports.
from textual import on
from textual.message import Message
from textual.widgets import OptionList
from textual.widgets.option_list import Option, Separator

##############################################################################
# Local imports.
from .bookmarks import Bookmarks


##############################################################################
class Menu(OptionList):
    """The main menu for the application."""

    _CORE_OPTIONS = ["All", "Unread", "Read", "Public", "Private", "Untagged", "Tagged"]
    """The core options of the menu."""

    _CORE_PREFIX = "core-"
    """The prefix given to each core filter option."""

    def refresh_options(self, bookmarks: Bookmarks | None = None) -> None:
        """Refresh the options in the menu.

        Args:
            bookmarks: The bookmarks to take data from.
        """
        options: list[Option | Separator] = [
            Option(prompt, id=f"{self._CORE_PREFIX}{prompt.lower()}")
            for prompt in self._CORE_OPTIONS
        ]
        if bookmarks:
            if tags := bookmarks.tags:
                options.append(Separator())
                options.extend(Option(tag, id=f"tag-{tag}") for tag in tags)
        self.clear_options().add_options(options)
        self.highlighted = 0

    def on_mount(self) -> None:
        """Initialise the menu once the DOM is ready."""
        self.refresh_options()

    class CoreFilter(Message, bubble=False):
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

    @on(OptionList.OptionSelected)
    def handle_selection(self, event: OptionList.OptionSelected) -> None:
        """Handle a menu option selection.

        Args:
            event: The event to handle.
        """
        event.stop()
        if event.option.id:
            if event.option.id.startswith(self._CORE_PREFIX):
                *_, core = event.option.id.partition(self._CORE_PREFIX)
                self.post_message(
                    {
                        "all": self.ShowAll,
                        "unread": self.ShowUnread,
                        "read": self.ShowRead,
                        "public": self.ShowPublic,
                        "private": self.ShowPrivate,
                        "tagged": self.ShowTagged,
                        "untagged": self.ShowUntagged,
                    }[core]()
                )


### menu.py ends here
