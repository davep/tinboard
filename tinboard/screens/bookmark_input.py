"""Provides a dialog for editing bookmark details."""

##############################################################################
# Backward compatibility.
from __future__ import annotations

##############################################################################
# Python imports.
from datetime import datetime
from urllib.parse import urlparse

##############################################################################
# Pyperclip imports.
from pyperclip import paste as from_clipboard, PyperclipException

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.events import DescendantBlur, DescendantFocus
from textual.screen import ModalScreen
from textual.validation import Length
from textual.widgets import Button, Checkbox, Input, Label

##############################################################################
# Local imports.
from ..pinboard import API, BookmarkData
from ..suggestions import SuggestTags
from ..widgets import TextArea


##############################################################################
class BookmarkInput(ModalScreen[BookmarkData | None]):
    """The bookmark editing dialog."""

    DEFAULT_CSS = """
    BookmarkInput {
        align: center middle;

        Vertical {
            width: 60%;
            height: auto;
            background: $surface;
            border: panel $primary;
            border-title-color: $accent;
        }

        #description {
            height: 10;
        }

        #buttons {
            height: auto;
            margin-top: 1;
            align-horizontal: right;
        }

        Button {
            margin-right: 1;
        }

        Label {
            margin: 1 0 0 1;
        }

        #flags {
            height: auto;
            margin-top: 1;
        }

        #tag-suggestions {
            display: none;
            width: 1fr;

            &.got-suggestions {
                display: block;
            }
        }
    }
    """

    BINDINGS = [("escape", "cancel"), ("f2", "save")]

    def __init__(
        self,
        api: API,
        bookmark: BookmarkData | None = None,
        *,
        known_tags: list[str] | None = None,
    ) -> None:
        """Initialise the bookmark input dialog.

        Args:
            api: The Pinboard API object.
            bookmark: The bookmark to edit, or `None` for a new one.
            known_tags: The tags we currently know about.
        """
        super().__init__()
        self._api = api
        self._last_url = "" if bookmark is None else bookmark.href
        self._bookmark = bookmark
        self._tags = known_tags or []

    def compose(self) -> ComposeResult:
        """Compose the layout of the dialog."""
        with Vertical() as dialog:
            dialog.border_title = "Bookmark"
            yield Label("URL:")
            yield Input(
                placeholder="Bookmark URL", id="url", validators=[Length(minimum=1)]
            )
            yield Label("Title:")
            yield Input(placeholder="Bookmark title", id="title")
            yield Label("Description:")
            yield TextArea(id="description")
            yield Label("Tags:")
            yield Input(
                placeholder="Bookmark tags (space separated)",
                id="tags",
                suggester=SuggestTags(self._tags),
            )
            yield Label(id="tag-suggestions")
            with Horizontal(id="flags"):
                yield Checkbox("Private", id="private")
                yield Checkbox("Read Later", id="read-later")
            with Horizontal(id="buttons"):
                yield Button("Save [dim]\\[F2][/]", id="save")
                yield Button("Cancel [dim]\\[Esc][/]", id="cancel")

    @work(exclusive=True)
    async def _get_tag_suggestions(self) -> None:
        """Load up fresh tag suggestions based on the URL."""
        try:
            tags = await self._api.suggested_tags(self.query_one("#url", Input).value)
        except API.Error:
            self.app.bell()
            self.notify(
                "Error getting suggested tags from the server.",
                title="Server Error",
                severity="error",
                timeout=8,
            )
            return
        suggested_tags = ""
        if tags.recommended:
            suggested_tags += f"[b]Recommended:[/b] {' '.join(tags.recommended)}\n"
        if tags.popular:
            suggested_tags += f"[b]Popular:[/b] {' '.join(tags.popular)}"
        self.query_one("#tag-suggestions").set_class(
            bool(suggested_tags.strip()), "got-suggestions"
        )
        self.query_one("#tag-suggestions", Label).update(f"[dim]{suggested_tags}[/]")
        self.query_one("#tags", Input).suggester = SuggestTags(
            set(self._tags + tags.recommended + tags.popular)
        )

    @work(thread=True)
    def _suggest_bookmark(self) -> None:
        """Get a bookmark suggestion by peeking in the clipboard."""
        try:
            clipboard = from_clipboard()
        except PyperclipException:
            return
        if clipboard:
            candidate = urlparse(clipboard)
            if candidate.scheme in ("http", "https"):

                def _paste():
                    url = self.query_one("#url", Input)
                    if not url.value:
                        url.value = clipboard
                        self._get_tag_suggestions()

                self.app.call_from_thread(_paste)

    def on_mount(self) -> None:
        """Configure the dialog once it's in the DOM."""
        if self._bookmark:
            self.query_one("#url", Input).value = self._bookmark.href
            self.query_one("#title", Input).value = self._bookmark.description
            self.query_one("#description", TextArea).text = self._bookmark.extended
            self.query_one("#tags", Input).value = self._bookmark.tags
            self.query_one("#private", Checkbox).value = not self._bookmark.shared
            self.query_one("#read-later", Checkbox).value = self._bookmark.to_read
            self._get_tag_suggestions()
        else:
            self._suggest_bookmark()

    @on(DescendantFocus, "#url")
    def _remember_url(self, event: DescendantFocus) -> None:
        """Save the URL on entry to the URL field.

        Args:
            event: The event to handle.
        """
        if isinstance(event.widget, Input):  # It should be, but help typing.
            self._last_url = event.widget.value.strip()

    @on(DescendantBlur, "#url")
    def _refresh_tag_suggestions(self, event: DescendantBlur) -> None:
        """Refresh the tag suggestions when leaving the URL field, having modified it."""
        if isinstance(event.widget, Input):  # It should be, but help typing.
            if (
                event.widget.value.strip()
                and event.widget.value.strip() != self._last_url
            ):
                self.query_one("#tag-suggestions").set_class(False, "got-suggestions")
                self._get_tag_suggestions()

    @on(Button.Pressed, "#save")
    def action_save(self) -> None:
        """Save the bookmark data."""
        if not self.query_one("#url", Input).value.strip():
            self.app.bell()
            self.notify(
                "The URL is required for the bookmark.",
                severity="error",
                title="Missing URL",
            )
            return
        self.dismiss(
            BookmarkData(
                href=self.query_one("#url", Input).value,
                description=self.query_one("#title", Input).value,
                extended=self.query_one("#description", TextArea).text,
                tags=self.query_one("#tags", Input).value,
                shared=not self.query_one("#private", Checkbox).value,
                to_read=self.query_one("#read-later", Checkbox).value,
                hash="" if self._bookmark is None else self._bookmark.hash,
                time=datetime.now() if self._bookmark is None else self._bookmark.time,
            )
        )

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        """Cancel the edit of the bookmark data."""
        self.dismiss(None)


### bookmark_input.py ends here
