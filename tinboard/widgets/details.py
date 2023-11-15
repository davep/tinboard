"""The details display widget."""

##############################################################################
# Python imports.
from dataclasses import dataclass
from webbrowser import open as open_url

##############################################################################
# Humanize imports.
from humanize import naturaltime

##############################################################################
# Textual imports.
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.message import Message
from textual.reactive import var
from textual.widgets import Label

##############################################################################
# Local imports.
from .bookmarks import Bookmark


##############################################################################
class Details(VerticalScroll):
    """A widget for displaying details of a bookmark."""

    DEFAULT_CSS = """
    Details {
        scrollbar-gutter: stable;
    }

    Details .hidden {
        visibility: hidden;
    }

    Details .empty {
        display: none;
    }

    Details Label {
        margin: 0 2 1 2;
        width: 1fr;
        color: $text;
    }

    Details #title {
        background: $primary;
        padding: 1 2 1 2;
        text-align: center;
    }

    Details .detail {
        background: $boost;
        padding: 1 2 1 2;
    }

    Details #last-modified-ish {
        margin: 0 2 0 2;
        padding: 1 2 0 2;
    }

    Details #last-modified-exact {
        margin: 0 2 1 2;
        padding: 0 2 1 2;
        text-align: right;
        color: $text-muted;
        text-style: italic;
    }
    """

    BINDINGS = [Binding("enter", "visit_bookmark", "Visit")]

    bookmark: var[Bookmark | None] = var(None)
    """The current bookmark."""

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Label(id="title")
        yield Label(id="description", classes="detail")
        yield Label(id="link", classes="detail")
        yield Label(id="last-modified-ish", classes="detail")
        yield Label(id="last-modified-exact", classes="detail")
        yield Label(id="is-read", classes="detail")
        yield Label(id="is-public", classes="detail")
        yield Label("TODO: Tags")

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
        try:
            if self.bookmark is None:
                return
            self.query_one("#title", Label).update(self.bookmark.title)
            self.query_one("#description", Label).update(self.bookmark.description)
            self.query_one("#description", Label).set_class(
                not bool(self.bookmark.description), "empty"
            )
            # TODO: This doesn't find the correct action.
            self.query_one("#link", Label).update(
                f"[@click=visit_bookmark]{self.bookmark.href}[/]"
            )
            self.query_one("#last-modified-ish", Label).update(
                f"Last updated {naturaltime(self.bookmark.last_modified)}"
            )
            self.query_one("#last-modified-exact", Label).update(
                str(self.bookmark.last_modified)
            )
            self.query_one("#is-read", Label).update(
                f"The bookmark has {'[i]not[/] ' if self.bookmark.unread else ''}been read"
            )
            self.query_one("#is-public", Label).update(
                f"The bookmark is {'[bold]public[/]' if self.bookmark.shared else '[dim]private[/]'}"
            )
        finally:
            self.query("*").set_class(not bool(self.bookmark), "hidden")

    def action_visit_bookmark(self) -> None:
        """Visit the current bookmark, if there is one."""
        if self.bookmark is not None:
            open_url(self.bookmark.href)

    @dataclass
    class ShowTaggedWith(Message):
        """Message to request that the bookmarks filter on a tag."""

        tag: str
        """The tag to filter the bookmarks with."""

    # @on(Markdown.LinkClicked)
    # def visit_link(self, event: Markdown.LinkClicked) -> None:
    #     """Visit any link clicked on the markdown.

    #     Args:
    #         event: The click event.
    #     """
    #     if event.href.startswith("tag:"):
    #         *_, tag = event.href.partition("tag:")
    #         self.post_message(self.ShowTaggedWith(tag))
    #     else:
    #         open_url(event.href)


### details.py ends here
