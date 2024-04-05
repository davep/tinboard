"""The main entry point for the application."""

##############################################################################
# Python imports.
from argparse import ArgumentParser, Namespace

##############################################################################
# Textual imports.
from textual import __version__ as __textual_version__

##############################################################################
# Local imports.
from . import __version__
from .app import Tinboard
from .data import ExitStates
from .widgets import Filters


##############################################################################
def get_args() -> Namespace:
    """Get the command line arguments.

    Returns:
        The parsed command line arguments.
    """
    parser = ArgumentParser(
        prog="tinboard",
        description="A terminal-based client for Pinboard.",
        epilog=f"v{__version__}",
    )

    # Add the add command
    parser.add_argument(
        "command",
        choices=["add"],
        nargs="?",
        help="A command to modify the startup behaviour",
    )

    # Add --filter
    parser.add_argument(
        "-f",
        "--filter",
        choices=Filters.core_filter_names(),
        default=Filters.core_filter_names()[0],
        help="Set the default filter to use on startup",
    )

    # Add --version
    parser.add_argument(
        "-v",
        "--version",
        help="Show version information.",
        action="version",
        version=f"%(prog)s {__version__} (Textual v{__textual_version__})",
    )

    # Return the arguments.
    return parser.parse_args()


##############################################################################
def run() -> None:
    """Run the application."""
    args = get_args()
    state = Tinboard(args.filter).run(inline=args.command == "add")
    if state == ExitStates.TOKEN_FORGOTTEN:
        if Tinboard.environmental_token():
            print(
                "It looks like your token is held in an environment variable. "
                "If you wish to have that forgotten you will need to remove it yourself."
            )
        else:
            print("The locally-held copy of your API token has been removed.")
    elif state == ExitStates.TOKEN_NEEDED:
        print("An API token is needed to be able to connect to Pinboard.")
    elif state == ExitStates.INLINE_SAVE_ERROR:
        print("There was an error writing the bookmark to the Pinboard server.")


##############################################################################
if __name__ == "__main__":
    run()

### __main__.py ends here
