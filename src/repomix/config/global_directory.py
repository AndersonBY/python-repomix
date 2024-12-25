"""
Global Directory Module - Manage Global Configuration Directory
"""

import os
import platform
from pathlib import Path


def get_global_directory() -> str:
    """Get global configuration directory

    Returns:
        Path to the global configuration directory
    """
    system = platform.system()

    if system == "Windows":
        # Windows: %APPDATA%/repomix
        appdata = Path(os.environ.get("APPDATA", "~"))
        if str(appdata) == "~":
            appdata = Path.home()
        return str(appdata / "repomix")

    elif system == "Darwin":
        # macOS: ~/Library/Application Support/repomix
        return str(Path.home() / "Library" / "Application Support" / "repomix")

    else:
        # Linux/Unix: ~/.config/repomix
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config_home:
            base_dir = Path(xdg_config_home)
        else:
            base_dir = Path.home() / ".config"
        return str(base_dir / "repomix")


def ensure_global_directory() -> None:
    """Ensure global configuration directory exists

    Creates the directory if it does not exist
    """
    directory = Path(get_global_directory())
    directory.mkdir(parents=True, exist_ok=True)


def get_global_config_path() -> str:
    """Get global configuration file path

    Returns:
        Full path to the global configuration file
    """
    return str(Path(get_global_directory()) / "repomix.config.json")
