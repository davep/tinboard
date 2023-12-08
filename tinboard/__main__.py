"""The main entry point for the application."""

##############################################################################
# Local imports.
from .app import Tinboard
from .data import ExitStates


##############################################################################
def run() -> None:
    """Run the application."""
    state = Tinboard().run()
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


##############################################################################
if __name__ == "__main__":
    run()

### __main__.py ends here
