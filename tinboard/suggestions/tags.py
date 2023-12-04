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

    def __init__(
        self,
        tags: Iterable[str],
        *,
        use_cache: bool = True,
        case_sensitive: bool = False,
    ) -> None:
        """Initialise the suggester.

        Args:
            tags: The collection of tags to suggest from.
            use_cache: Should a cache be used?
            case_sensitive: Should the check be case sensitive?
        """
        super().__init__(use_cache=use_cache, case_sensitive=case_sensitive)
        self._tags = list(tags)
        self._candidates = (
            self._tags
            if self.case_sensitive
            else [candidate.casefold() for candidate in self._tags]
        )

    _LAST_WORD: Final[Pattern[str]] = re.compile(r"\S+$")
    """Regular expression to find the last word in a string."""

    async def get_suggestion(self, value: str) -> str | None:
        """Get suggestions for the given value.

        Args:
            value: The value to make a suggestion for.

        Returns:
            A suggested completion, or `None` if none could be made.
        """
        # TODO: Don't suggest a tag that's already in the value.
        if last_word := self._LAST_WORD.search(value):
            for candidate in self._candidates:
                if candidate.startswith(last_word[0]):
                    return value[: -len(last_word[0])] + candidate
        return None


### tags.py ends here
