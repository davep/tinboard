"""Commands related to modifying bookmarks."""

##############################################################################
# Python imports.
from functools import partial

##############################################################################
# Textual imports.
from textual.command import Hit, Hits, Provider

##############################################################################
# Local imports.
from ..messages import (
    AddBookmark,
    EditBookmark,
    ToggleBookmarkPublic,
    ToggleBookmarkRead,
)


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
            (
                "Add a new bookmark",
                AddBookmark,
                "Add a new bookmark to your bookmark collection",
            ),
            ("Edit bookmark", EditBookmark, "Edit the current bookmark"),
            (
                "Toggle public/private",
                ToggleBookmarkPublic,
                "Toggle the current bookmark's public/private status",
            ),
            (
                "Toggle read/unread",
                ToggleBookmarkRead,
                "Toggle the current bookmark's read/unread status",
            ),
        ):
            if match := matcher.match(command):
                yield Hit(
                    match,
                    matcher.highlight(command),
                    partial(self.screen.post_message, message()),
                    help=help_text,
                )


### bookmark_modification.py ends here
