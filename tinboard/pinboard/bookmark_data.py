"""Provides a class for holding data on a bookmark."""

##############################################################################
# Python imports.
from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import md5
from typing import Any, Callable

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

        # An accident of how this developed means that the Pinboard API
        # calls this `toread`, but I locally call it `to_read`, and I ended
        # up using the same code to pull the data back from JSON. So...
        if (to_read := "to_read") not in data:
            to_read = "toread"

        return cls(
            href=data.get("href", ""),
            description=data.get("description", ""),
            extended=data.get("extended", ""),
            hash=data.get("hash", ""),
            time=parse_time(data.get("time", "")),
            shared=boolify(data.get("shared", "")),
            to_read=boolify(data.get(to_read, "")),
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

    @property
    def has_tags(self) -> bool:
        """Does the bookmark have any tags?"""
        return bool(self.tag_list)

    def is_tagged(self, *tags: str) -> bool:
        """Is this bookmark tagged with the given tags?

        Args:
            tags: The tags to check for.

        Returns:
            `True` if the bookmark has all the tags, `False` if not.
        """
        return {tag.casefold() for tag in tags}.issubset(
            {tag.casefold() for tag in self.tag_list}
        )

    def has_text(self, search_text: str) -> bool:
        """Does the bookmark contain the given text?

        Note that this is a case-insensitive test.

        Args:
            search_text: The text to search for.

        Returns:
            `True` if the text was found anywhere in the bookmark, `False`
            if not.
        """
        return (
            search_text.casefold()
            in f"{self.description} {self.extended} {self.tags}".casefold()
        )

    def is_all(self, *checks: Callable[["BookmarkData"], bool]) -> bool:
        """Does this bookmark pass all the given tests?

        Args:
            checks: The checks to run against the bookmark.

        Returns:
            `True` if all tests pass, `False` if not.
        """
        return all(check(self) for check in checks)


### bookmark_data.py ends here
