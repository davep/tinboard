"""Defines the main menu for the application."""

##############################################################################
# Textual imports.
from textual.widgets import OptionList


##############################################################################
class Menu(OptionList):
    """The main menu for the application."""

    def on_mount(self) -> None:
        """Populate the menu."""
        self.add_options(["All", "Unread", "Public", "Private", "Untagged", "Tagged"])
        self.highlighted = 0


### menu.py ends here
