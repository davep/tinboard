"""A version of Textual's OptionList with some more navigation options."""

##############################################################################
# Python imports.
from typing_extensions import Self

##############################################################################
# Textual imports.
from textual.binding import Binding
from textual.widgets import OptionList


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
