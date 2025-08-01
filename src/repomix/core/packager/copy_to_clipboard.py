"""
Copy to Clipboard Module - Handles copying content to system clipboard
"""

import os
import shutil
import subprocess

import pyperclip

from ...config.config_schema import RepomixConfig
from ...shared.logger import logger


def copy_to_clipboard_if_enabled(output: str, config: RepomixConfig) -> None:
    """Copy output to clipboard if enabled in config.

    Args:
        output: The content to copy to clipboard
        config: Repomix configuration

    Raises:
        Exception: If clipboard operation fails
    """
    if not config.output.copy_to_clipboard:
        return

    logger.info("Copying to clipboard...")

    # Check for Wayland display first (Linux)
    if os.environ.get("WAYLAND_DISPLAY") and shutil.which("wl-copy"):
        logger.trace("Wayland detected; attempting wl-copy.")
        try:
            subprocess.run(
                ["wl-copy"],
                input=output,
                text=True,
                capture_output=True,
                check=True,
            )
            logger.trace("Copied using wl-copy.")
            return
        except subprocess.CalledProcessError as e:
            logger.warn(f"wl-copy failed (exit code {e.returncode}); falling back.")
        except FileNotFoundError:
            logger.warn("wl-copy not found; falling back.")

    # Fallback to pyperclip
    try:
        logger.trace("Using pyperclip.")
        pyperclip.copy(output)
        logger.trace("Copied using pyperclip.")
    except Exception as e:
        logger.error(f"pyperclip failed: {e}")
        raise
