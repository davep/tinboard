"""Pinboard returns an empty list when it has no tag suggestions for a URL."""

##############################################################################
# Python imports.
import asyncio
from typing import Any

##############################################################################
# Local imports.
from tinboard.pinboard.api import API


##############################################################################
def test_suggested_tags_with_no_suggestions() -> None:
    """An empty suggestion list should give empty tags, not a TypeError."""
    api = API("user:TOKEN")

    async def fake_call(*path: str, **params: Any) -> str:
        return "[]"

    api._call = fake_call  # type: ignore[method-assign]
    suggestions = asyncio.run(api.suggested_tags("https://example.com/"))
    assert suggestions.url == "https://example.com/"
    assert suggestions.popular == []
    assert suggestions.recommended == []


### test_suggest_empty.py ends here
