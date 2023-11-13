"""Defines the main menu for the application."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Textual imports.
from textual.widgets import OptionList
from textual.widgets.option_list import Option, Separator

##############################################################################
# Local imports.
from .bookmarks import Bookmarks


##############################################################################
class Menu(OptionList):
    """The main menu for the application."""

    _CORE_OPTIONS = ["All", "Unread", "Public", "Private", "Untagged", "Tagged"]
    """The core options of the menu."""

    def refresh_options(self, bookmarks: Bookmarks | None = None) -> None:
        """Refresh the options in the menu.

        Args:
            bookmarks: The bookmarks to take data from.
        """
        options: list[Option | Separator] = [
            Option(prompt, id=f"core-{prompt.lower()}") for prompt in self._CORE_OPTIONS
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


### menu.py ends here
