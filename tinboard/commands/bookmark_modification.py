"""Commands related to modifying bookmarks."""

##############################################################################
# Python imports.
from functools import partial

##############################################################################
# Textual imports.
from textual.command import Hit, Hits, Provider

##############################################################################
# Local imports.
from ..messages import EditBookmark


##############################################################################
class BookmarkModificationCommands(Provider):
    """A source of commands for making modifications to bookmarks."""

    async def search(self, query: str) -> Hits:
        """Handle a request to search for commands that match the query.

        Args:
            query: The query from the user.

        Yields:
            Command hits for the command palette.
        """
        matcher = self.matcher(query)
        for command, message, help_text in (
            ("Edit bookmark", EditBookmark, "Edit the current bookmark"),
        ):
            if match := matcher.match(command):
                yield Hit(
                    match,
                    matcher.highlight(command),
                    partial(self.screen.post_message, message()),
                    help=help_text,
                )


### bookmark_modification.py ends here
