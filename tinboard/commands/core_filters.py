"""Core filtering commands for the command palette."""

##############################################################################
# Python imports.
from functools import partial

##############################################################################
# Textual imports.
from textual.command import Hit, Hits, Provider

##############################################################################
# Local imports.
from ..widgets import Filters


##############################################################################
class CoreFilteringCommands(Provider):
    """A source of commands for invoking the core filters."""

    async def search(self, query: str) -> Hits:
        """Handle a request to search for commands that match the query.

        Args:
            query: The query from the user.

        Yields:
            Command hits for the command palette.
        """
        matcher = self.matcher(query)
        for command in Filters.OPTIONS:
            full_command = f"Show {command}"
            if match := matcher.match(full_command):
                yield Hit(
                    match,
                    matcher.highlight(full_command),
                    partial(
                        self.screen.post_message,
                        Filters.core_filter_message(command),
                    ),
                    help=(
                        "Show all bookmarks"
                        if command == "All"
                        else f"Show all bookmarks that are {command.lower()}"
                    ),
                )


### core_filters.py ends here
