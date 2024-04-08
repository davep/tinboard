"""Provides a function for parsing time."""

##############################################################################
# Python imports.
from datetime import datetime


##############################################################################
def parse_time(text: str) -> datetime:
    """Parse a time from the Pinboard API.

    Args:
        text: The text version of the time to parse.

    Returns:
        The parsed time.

    Pinboard returns times ending in a `Z`. Python doesn't seem capable of
    parsing that. So we swap that for a `+00:00` and then parse.
    """
    return datetime.fromisoformat(
        (text.removesuffix("Z") + "+00:00") if "Z" in text else text
    )


### parse_time.py ends here
