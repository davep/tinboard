"""Dialog for checking if a bookmark is in the Wayback Machine."""

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.reactive import var
from textual.screen import ModalScreen
from textual.widgets import Button, Label

##############################################################################
# Local imports.
from ..wayback import Availability, WaybackError, availability


##############################################################################
class WaybackChecker(ModalScreen[None]):
    """Dialog for checking if a URL is in the Wayback machine."""

    CSS = """
    WaybackChecker {
        align: center middle;

        &> Vertical {
            height: auto;
            width: auto;
            background: $surface;
            border: panel $primary;
            border-title-color: $accent;

            Label {
                height: auto;
                padding: 1 1 0 1;
                margin-bottom: 1;
            }

            Center {
                width: 100%;
            }
        }

        &.not-available > Vertical {
            border: panel $warning;
        }

        &.error > Vertical {
            border: panel $error;
        }

        &.loading > Vertical {
            min-width: 50vw;
            min-height: 15;
        }
    }
    """

    BINDINGS = [("escape", "close")]

    _wayback_data: var[Availability | WaybackError | None] = var(None, init=False)
    """The wayback availability data."""

    def __init__(self, url: str) -> None:
        """Initialise the dialog."""
        super().__init__(classes="loading")
        self._url = url

    def on_mount(self) -> None:
        """Once the DOM is ready, start looking up the URL."""
        self.check_availability()

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog") as dialog:
            dialog.loading = True
            dialog.border_title = "Wayback Machine"
            yield Label("Loading...")
            with Center():
                yield Button("OK")

    @work
    async def check_availability(self) -> None:
        """Check if the given URL is available in the Wayback Machine."""
        try:
            self._wayback_data = await availability(self._url)
        except WaybackError as error:
            self._wayback_data = error
        finally:
            self.set_class(False, "loading")
            self.query_one("#dialog").loading = False

    def _watch__wayback_data(self) -> None:
        """React to the data coming back from the Wayback Machine."""
        if self._wayback_data is None:
            return
        if isinstance(self._wayback_data, WaybackError):
            self.query_one(Label).update(
                f"Error talking to the Wayback Machine.\n\n{self._wayback_data}"
            )
            self.query_one("#dialog", Vertical).set_class(True, "error")
            return
        if self._wayback_data.available:
            self.query_one(Label).update(
                "The bookmark is available in the Wayback machine.\n\n"
                f"It was last archived {self._wayback_data.timestamp}."
            )
        else:
            self.query_one(Label).update(
                "The bookmark is not available in the Wayback machine."
            )
            self.set_class(True, "not-available")

    @on(Button.Pressed)
    def action_close(self) -> None:
        """Close the help screen."""
        self.dismiss(None)


### wayback_checker.py ends here
