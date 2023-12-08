"""Defines exit states for the application."""

##############################################################################
# Python imports.
from enum import Enum


##############################################################################
class ExitStates(Enum):
    """Exit states for the application."""

    OKAY = 0
    """The general exit state."""

    TOKEN_NEEDED = 1
    """The application exited because a token is needed and none was given."""

    TOKEN_FORGOTTEN = 2
    """The application exited because the user forgot the token."""


### exit_states.py ends here
