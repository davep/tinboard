"""Provides a class for holding data on a bookmark."""

##############################################################################
# Python imports.
from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import md5
from typing import Any

##############################################################################
# Local imports.
from .parse_time import parse_time


##############################################################################
@dataclass
class BookmarkData:
    """Pinboard bookmark data."""

    href: str
    """The URL for the bookmark."""

    description: str
    """The description (AKA title) of the bookmark."""

    extended: str
    """The extended description of the bookmark."""

    hash: str
    """The hash for the bookmark."""

    time: datetime
    """The time of the bookmark's modification."""

    shared: bool
    """Is the bookmark shared with the public?"""

    to_read: bool
    """Is the bookmark unread?"""

    tags: str
    """The tags for the bookmark, space-separated."""

    def __post_init__(self) -> None:
        """Final initialisation of the bookmark data.

        If `hash` is empty, one will be generated.
        """
        if not self.hash:
            self.hash = md5(self.href.encode()).hexdigest()

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "BookmarkData":
        """Create an instance of `BookmarkData` from JSON data.

        Args:
            data: The data to create the bookmark instance from.

        Returns:
            An instance of `BookmarkData`.
        """

        def boolify(value: str | bool) -> bool:
            return value == "yes" if isinstance(value, str) else value

        return cls(
            href=data.get("href", ""),
            description=data.get("description", ""),
            extended=data.get("extended", ""),
            hash=data.get("hash", ""),
            time=parse_time(data.get("time", "")),
            shared=boolify(data.get("shared", "")),
            to_read=boolify(data.get("toread", "")),
            tags=data.get("tags", ""),
        )

    @property
    def as_json(self) -> dict[str, str]:
        """The bookmark in JSON-friendly form."""
        return asdict(self)

    @property
    def tag_list(self) -> list[str]:
        """The tags as a list of individual tags."""
        return self.tags.split()


### bookmark_data.py ends here
