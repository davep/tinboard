"""Core commands for the application."""

##############################################################################
# Python imports.
from functools import partial

##############################################################################
# Textual imports.
from textual.command import DiscoveryHit, Hit, Hits, Provider

##############################################################################
# Backward-compatible typing.
from typing_extensions import Final


##############################################################################
class CoreCommands(Provider):
    """A source of commands for invoking the main application commands."""

    COMMANDS: Final[tuple[tuple[str, str, str], ...]] = (
        ("Help", "help", "Show the main help screen"),
        ("Visit Pinboard", "goto_pinboard", "Visit the Pinboard website"),
        (
            "Redownload/refresh bookmarks",
            "redownload",
            "Download a full fresh copy of your bookmarks from Pinboard",
        ),
        ("Search", "search", "Search for text in the currently-shown bookmarks"),
        (
            "Logout",
            "logout",
            "Forget your Pinboard API token and remove the local copies of all bookmarks.",
        ),
        (
            "Toggle details",
            "toggle_details",
            "Toggle the display of the details of the highlighted bookmark.",
        ),
    )

    async def discover(self) -> Hits:
        """Handle a request to discover commands.

        Yields:
            Command discovery hits for the command palette.
        """
        for command, action, help_text in self.COMMANDS:
            yield DiscoveryHit(
                command,
                partial(self.screen.run_action, action),
                help=help_text,
            )

    async def search(self, query: str) -> Hits:
        """Handle a request to search for commands that match the query.

        Args:
            query: The query from the user.

        Yields:
            Command hits for the command palette.
        """
        matcher = self.matcher(query)
        for command, action, help_text in self.COMMANDS:
            if match := matcher.match(command):
                yield Hit(
                    match,
                    matcher.highlight(command),
                    partial(self.screen.run_action, action),
                    help=help_text,
                )


### core_commands.py ends here
