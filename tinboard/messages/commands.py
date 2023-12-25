"""Provides system-command level message classes."""

##############################################################################
# Textual imports.
from textual.message import Message


##############################################################################
class Command(Message):
    """Base class for all command-oriented messages."""


##############################################################################
class AddBookmark(Command):
    """Add a new bookmark."""


##############################################################################
class EditBookmark(Command):
    """Edit the current bookmark."""


##############################################################################
class DeleteBookmark(Command):
    """Delete the current bookmark."""


##############################################################################
class ToggleBookmarkRead(Command):
    """Toggle the read status of the current bookmark."""


##############################################################################
class ToggleBookmarkPublic(Command):
    """Toggle the public status of the current bookmark."""


##############################################################################
class CopyBookmarkURL(Command):
    """Copy the URL for the bookmark to the clipboard."""


### commands.py ends here
