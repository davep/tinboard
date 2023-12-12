"""The details display widget."""

##############################################################################
# Python imports.
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
from ..messages import EditBookmark, ToggleBookmarkPublic, ToggleBookmarkRead
from .bookmarks import Bookmark
from .tags import InlineTags


##############################################################################
class Link(Label):
    """Widget for showing the link.

    This is here mostly to work around the fact that a click action doesn't
    propagate in the way you'd expect.

    https://github.com/Textualize/textual/issues/3690
    """

    class Visit(Message):
        """Message to indicate that the link should be visited."""

    def action_visit(self) -> None:
        """Handle a UI request to visit the link."""
        self.post_message(self.Visit())


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

    Details #added-ish {
        margin: 0 2 0 2;
        padding: 1 2 0 2;
    }

    Details #added-exact {
        margin: 0 2 1 2;
        padding: 0 2 1 2;
        text-align: right;
        color: $text-muted;
        text-style: italic;
    }

    Details InlineTags, Details InlineTags:focus {
        margin: 0 2 1 2;
    }
    """

    BINDINGS = [
        Binding("e", "edit", "Edit Bookmark"),
        Binding("ctrl+r", "read", "(Un)Read"),
        Binding("ctrl+v", "public", "Public/Private"),
        Binding("enter", "visit_bookmark", "Visit Bookmark"),
    ]

    bookmark: var[Bookmark | None] = var(None, always_update=True)
    """The current bookmark."""

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Label(id="title")
        yield Label(id="description", classes="detail empty")
        yield Link(id="link", classes="detail")
        yield Label(id="added-ish", classes="detail")
        yield Label(id="added-exact", classes="detail")
        yield Label(id="is-read", classes="detail")
        yield Label(id="is-public", classes="detail")
        yield InlineTags(classes="empty")

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
            self.query_one(Link).update(f"[@click=visit]{self.bookmark.href}[/]")
            self.query_one("#added-ish", Label).update(
                f"Added {naturaltime(self.bookmark.last_modified)}"
            )
            self.query_one("#added-exact", Label).update(
                str(self.bookmark.last_modified)
            )
            self.query_one("#is-read", Label).update(
                f"The bookmark has {'[i]not[/] ' if self.bookmark.unread else ''}been read"
            )
            self.query_one("#is-public", Label).update(
                f"The bookmark is {'[bold]public[/]' if self.bookmark.shared else '[dim]private[/]'}"
            )
            self.query_one(InlineTags).show(
                [(tag, 1) for tag in sorted(self.bookmark.tags, key=str.casefold)]
            ).set_class(not bool(self.bookmark.tags), "empty")

        finally:
            self.query("*").set_class(not bool(self.bookmark), "hidden")

    def action_edit(self) -> None:
        """Post the edit command."""
        self.post_message(EditBookmark())

    def action_read(self) -> None:
        """Post the read status toggle command."""
        self.post_message(ToggleBookmarkRead())

    def action_public(self) -> None:
        """Post the public/private toggle command."""
        self.post_message(ToggleBookmarkPublic())

    @on(Link.Visit)
    def action_visit_bookmark(self) -> None:
        """Visit the current bookmark, if there is one."""
        if self.bookmark is not None:
            open_url(self.bookmark.href)


### details.py ends here
