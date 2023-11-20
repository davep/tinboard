"""Tag filtering commands for the command palette."""

##############################################################################
# Python imports.
from functools import partial
from typing import Callable

##############################################################################
# Textual imports.
from textual.command import Hit, Hits, Provider


##############################################################################
class TagCommands(Provider):
    """A source of commands for filtering bookmarks by tag."""

    current_tags: list[str] = []
    """The current set of tags to draw on when setting up the commands."""

    show_tagged: Callable[[str], None] | None = None
    """The method to call to show bookmarks tagged with a given tag."""

    show_also_tagged: Callable[[str], None] | None = None
    """The method to call to show bookmarks also tagged with a given tag."""

    async def search(self, query: str) -> Hits:
        """Handle a request to search for commands that match the query.

        Args:
            query: The query from the user.

        Yields:
            Command hits for the command palette.
        """
        assert self.show_tagged is not None and self.show_also_tagged is not None
        matcher = self.matcher(query)
        for tag in self.current_tags:
            for prefix, call in (
                ("", self.show_tagged),
                ("Also", self.show_also_tagged),
            ):
                full_command = f"{prefix} tagged {tag}".strip().capitalize()
                if match := matcher.match(full_command):
                    yield Hit(
                        match,
                        matcher.highlight(full_command),
                        partial(call, tag),
                        help=f"Show all bookmarks that are {full_command.lower()}",
                    )


### tags.py ends here
