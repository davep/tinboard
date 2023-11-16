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
from textual.widgets import Label, OptionList
from textual.widgets.option_list import Option

##############################################################################
# Local imports.
from .bookmarks import Bookmark


##############################################################################
class Tags(OptionList):
    """A widget for displaying tags."""

    BINDINGS = [
        Binding("enter", "select", "Show tagged", show=True),
        Binding("+", "also_tagged", "Show also tagged"),
    ]

    def on_focus(self) -> None:
        """Ensure that something is highlighted, if possible"""
        if self.option_count and self.highlighted is None:
            self.highlighted = 0

    @dataclass
    class ShowAlsoTaggedWith(Message):
        """Message to request that the bookmarks filter also include this tag."""

        tag: str
        """The tag to add to the filter."""

    def action_also_tagged(self) -> None:
        """Handle a request to add a tag to a tag filter."""
        if self.highlighted is not None:
            if (tag := self.get_option_at_index(self.highlighted).id) is not None:
                self.post_message(self.ShowAlsoTaggedWith(tag))


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

    Details Tags, Details Tags:focus {
        border: blank;
        margin: 0 2 1 2;
    }
    """

    BINDINGS = [Binding("enter", "visit_bookmark", "Visit")]

    bookmark: var[Bookmark | None] = var(None)
    """The current bookmark."""

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Label(id="title")
        yield Label(id="description", classes="detail empty")
        yield Label(id="link", classes="detail")
        yield Label(id="last-modified-ish", classes="detail")
        yield Label(id="last-modified-exact", classes="detail")
        yield Label(id="is-read", classes="detail")
        yield Label(id="is-public", classes="detail")
        yield Tags(classes="empty")

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
            self.query_one(Tags).clear_options().add_options(
                [
                    Option(tag, id=tag)
                    for tag in sorted(self.bookmark.tags, key=str.casefold)
                ]
            ).set_class(not bool(self.bookmark.tags), "empty")

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

    @on(Tags.OptionSelected)
    def show_tagged(self, event: Tags.OptionSelected) -> None:
        """Request that bookmarks with this tag be shown."""
        if event.option_id is not None:
            self.post_message(self.ShowTaggedWith(event.option_id))

    @dataclass
    class ShowAlsoTaggedWith(Message):
        """Message to request that the bookmarks filter also include this tag."""

        tag: str
        """The tag to add to the filter."""

    @on(Tags.ShowAlsoTaggedWith)
    def show_also_tagged(self, event: Tags.ShowAlsoTaggedWith) -> None:
        """Request that a tag be added to any existing tag filter."""
        self.post_message(self.ShowAlsoTaggedWith(event.tag))


### details.py ends here
