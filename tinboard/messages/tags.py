"""Provides tag-related messages."""

##############################################################################
# Python imports.
from dataclasses import dataclass

##############################################################################
# Textual imports.
from textual.message import Message


##############################################################################
@dataclass
class TagMessage(Message):
    """Base class for the tag messages."""

    tag: str
    """The tag associated with the message."""


##############################################################################
class ShowTaggedWith(TagMessage):
    """Message to say bookmarks of this tag should be shown."""


##############################################################################
class ShowAlsoTaggedWith(TagMessage):
    """Message to say bookmarks also of this tag should be shown."""


### tags.py ends here
