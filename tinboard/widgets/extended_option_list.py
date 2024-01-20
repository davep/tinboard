"""A version of Textual's OptionList with some more navigation options."""

##############################################################################
# Textual imports.
from textual.binding import Binding
from textual.widgets import OptionList

##############################################################################
# Backward-compatible typing.
from typing_extensions import Self


##############################################################################
class OptionListEx(OptionList):
    """The Textual `OptionList` with more navigation keys."""

    BINDINGS = [
        Binding("s, j", "cursor_down", show=False),
        Binding("w, k", "cursor_up", show=False),
    ]

    def clear_options(self) -> Self:
        """Workaround for https://github.com/Textualize/textual/issues/3714"""
        super().clear_options()
        self._clear_content_tracking()
        return self


### extended_option_list.py ends here
