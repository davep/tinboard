"""Commands related to the list of bookmarks."""

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
    CopyBookmarkURL,
    EditBookmark,
    DeleteBookmark,
    ToggleBookmarkPublic,
    ToggleBookmarkRead,
)


##############################################################################
class BookmarkCommands(Provider):
    """A source of commands for doing things with bookmarks."""

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
            (
                "Copy to clipboard",
                CopyBookmarkURL,
                "Copy the URL for the current bookmark to the clipboard",
            ),
            ("Edit bookmark", EditBookmark, "Edit the current bookmark"),
            (
                "Toggle public/private",
                ToggleBookmarkPublic,
                "Toggle the current bookmark's public/private status",
            ),
            ("Delete bookmark", DeleteBookmark, "Delete the current bookmark"),
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


### bookmarks.py ends here
