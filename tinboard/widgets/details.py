"""The details display widget."""

##############################################################################
# Textual imports.
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Markdown

##############################################################################
# Local imports.
from .bookmarks import Bookmark


##############################################################################
class Details(VerticalScroll):
    """A widget for displaying details of a bookmark."""

    def compose(self) -> ComposeResult:
        yield Markdown()

    def show(self, bookmark: Bookmark) -> None:
        """Show the details for a given bookmark.

        Args:
            bookmark: The bookmark to show.
        """
        self.query_one(Markdown).update(
            f"# {bookmark.title}\n"
            f"{bookmark.description}\n"
            f"## Link\n[{bookmark.href}]({bookmark.href})\n"
            f"## Last Modified\n{bookmark.last_modified}\n"
            f"## Tags\n{bookmark.tags}\n"
            f"## Read\n{not bookmark.unread}\n"
            f"## Public\n{bookmark.shared}\n"
        )


### details.py ends here
