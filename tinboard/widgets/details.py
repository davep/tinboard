"""The details display widget."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from webbrowser import open as open_url

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import var
from textual.widgets import Markdown

##############################################################################
# Local imports.
from .bookmarks import Bookmark


##############################################################################
class Details(VerticalScroll):
    """A widget for displaying details of a bookmark."""

    BINDINGS = [Binding("enter", "visit_bookmark", "Visit")]

    bookmark: var[Bookmark | None] = var(None)
    """The current bookmark."""

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Markdown()

    @property
    def _tags(self) -> str:
        """The collection of tags as a displayable string."""
        return (
            ", ".join(
                f"[{tag}](tag:{tag})"
                for tag in sorted(self.bookmark.tags, key=str.casefold)
            )
            if self.bookmark is not None
            else ""
        )

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
                f"## Tags\n{self._tags}\n"
                f"## Read\n{not self.bookmark.unread}\n"
                f"## Public\n{self.bookmark.shared}\n"
            )
        )

    def action_visit_bookmark(self) -> None:
        """Visit the current bookmark, if there is one."""
        if self.bookmark is not None:
            open_url(self.bookmark.href)

    @dataclass
    class ShowTaggedWith(Message):
        """Message to request that the bookmarks filter on a tag."""

        tag: str
        """The tag to filter the bookmarks with."""

    @on(Markdown.LinkClicked)
    def visit_link(self, event: Markdown.LinkClicked) -> None:
        """Visit any link clicked on the markdown.

        Args:
            event: The click event.
        """
        if event.href.startswith("tag:"):
            *_, tag = event.href.partition("tag:")
            self.post_message(self.ShowTaggedWith(tag))
        else:
            open_url(event.href)


### details.py ends here
