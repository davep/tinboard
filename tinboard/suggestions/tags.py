"""Provides a suggester for tags."""

##############################################################################
# Python imports.
import re
from typing import Iterable, Pattern
from typing_extensions import Final

##############################################################################
# Textual imports.
from textual.suggester import Suggester


##############################################################################
class SuggestTags(Suggester):
    """A Textual `Input` suggester that suggests tags."""

    def __init__(self, tags: Iterable[str]) -> None:
        """Initialise the suggester.

        Args:
            tags: The collection of tags to suggest from.
        """
        # Note that we're going to be doing a case-insensitive match, but
        # the suggester API doesn't provided the raw value if you're not
        # being case-sensitive; so here we say we *are* going to be case
        # sensitive and then in get_suggestion we'll handle it ourselves.
        super().__init__(use_cache=True, case_sensitive=True)
        self._tags = list(tags)
        self._candidates = [candidate.casefold() for candidate in self._tags]

    _TAGS: Final[Pattern[str]] = re.compile(r"\s+")
    """Regular expression for splitting a string into individual tags."""

    _SUGGESTABLE: Final[Pattern[str]] = re.compile(r".*[^\s]$")
    """Regular expression to test if a value deserves a suggestion."""

    async def get_suggestion(self, value: str) -> str | None:
        """Get suggestions for the given value.

        Args:
            value: The value to make a suggestion for.

        Returns:
            A suggested completion, or `None` if none could be made.
        """
        if self._SUGGESTABLE.match(value):
            try:
                *other_tags, last_tag = [tag for tag in self._TAGS.split(value) if tag]
            except ValueError:
                return None
            used_tags = set(tag.casefold() for tag in other_tags)
            for candidate_index, candidate in enumerate(self._candidates):
                if candidate.startswith(last_tag) and candidate not in used_tags:
                    return value[: -len(last_tag)] + self._tags[candidate_index]
        return None


### tags.py ends here
