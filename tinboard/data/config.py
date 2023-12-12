"""Code relating to the application's configuration file."""

##############################################################################
# Python imports.
from dataclasses import dataclass, asdict
from functools import lru_cache
from json import dumps, loads
from pathlib import Path

##############################################################################
# Local imports.
from .locations import config_dir


##############################################################################
@dataclass
class Configuration:
    """The configuration data for the application."""

    dark_mode: bool = True
    """Should we run in dark mode?"""

    details_visible: bool = True
    """Show the details pane be visible?"""


##############################################################################
def configuration_file() -> Path:
    """The path to the file that holds the application configuration.

    Returns:
        The path to the configuration file.
    """
    return config_dir() / "configuration.json"


##############################################################################
def save_configuration(configuration: Configuration) -> Configuration:
    """Save the given configuration.

    Args:
        The configuration to store.

    Returns:
        The configuration.
    """
    load_configuration.cache_clear()
    configuration_file().write_text(
        dumps(asdict(configuration), indent=4), encoding="utf-8"
    )
    return load_configuration()


##############################################################################
@lru_cache(maxsize=None)
def load_configuration() -> Configuration:
    """Load the configuration.

    Returns:
        The configuration.

    Note:
        As a side-effect, if the configuration doesn't exist a default one
        will be saved to storage.

        This function is designed so that it's safe and low-cost to
        repeatedly call it. The configuration is cached and will only be
        loaded from storage when necessary.
    """
    source = configuration_file()
    return (
        Configuration(**loads(source.read_text(encoding="utf-8")))
        if source.exists()
        else save_configuration(Configuration())
    )


### config.py ends here
