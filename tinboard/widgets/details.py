"""The details display widget."""

##############################################################################
# Textual imports.
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import var
from textual.widgets import Markdown

##############################################################################
# Local imports.
from .bookmarks import Bookmark


##############################################################################
class Details(VerticalScroll):
    """A widget for displaying details of a bookmark."""

    bookmark: var[Bookmark | None] = var(None)
    """The current bookmark."""

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Markdown()

    def _watch_bookmark(self) -> None:
        """React to the bookmark being changed."""
        self.query_one(Markdown).update(
            ""
            if self.bookmark is None
            else (
                f"# {self.bookmark.title}\n"
                f"{self.bookmark.description}\n"
                f"## Link\n[{self.bookmark.href}]({self.bookmark.href})\n"
                f"## Last Modified\n{self.bookmark.last_modified}\n"
                f"## Tags\n{', '.join(self.bookmark.tags)}\n"
                f"## Read\n{not self.bookmark.unread}\n"
                f"## Public\n{self.bookmark.shared}\n"
            )
        )


### details.py ends here
