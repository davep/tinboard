"""Provides system-command level message classes."""

##############################################################################
# Textual imports.
from textual.message import Message


##############################################################################
class Command(Message):
    """Base class for all command-oriented messages."""


##############################################################################
class EditBookmark(Command):
    """Edit the current bookmark."""


##############################################################################
class ToggleBookmarkRead(Command):
    """Toggle the read status of the current bookmark."""


### commands.py ends here
