"""Provides a widget for displaying the bookmarks."""

##############################################################################
# Textual imports.
from textual.widgets import OptionList
from textual.widgets.option_list import Option


##############################################################################
class Bookmark(Option):
    """An individual bookmark."""


##############################################################################
class Bookmarks(OptionList):
    """The list of bookmarks."""


### bookmarks.py ends here
