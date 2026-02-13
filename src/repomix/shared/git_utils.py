"""
Git Utilities Module - Git related helper functions
"""

import re
from pathlib import Path

from ..shared.logger import logger
from ..shared.error_handle import RepomixError
from ..core.file.git_command import exec_git_shallow_clone


def format_git_url(url: str) -> str:
    """Format Git URL

    Args:
        url: Original URL

    Returns:
        Formatted URL
    """
    # If URL format is owner/repo, convert to GitHub URL
    if re.match(r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$", url):
        logger.trace(f"Formatting GitHub shorthand: {url}")
        return f"https://github.com/{url}.git"

    # If HTTPS URL without .git suffix, add .git
    if url.startswith("https://") and not url.endswith(".git"):
        logger.trace(f"Adding .git suffix to HTTPS URL: {url}")
        return f"{url}.git"

    return url


def clone_repository(url: str, directory: str | Path, branch: str | None = None) -> None:
    """Clone repository

    Args:
        url: Repository URL
        directory: Target directory
        branch: Branch name (optional)
    """
    # Clone repository
    formatted_url = format_git_url(url)

    try:
        exec_git_shallow_clone(formatted_url, directory, branch)
    except Exception as error:
        raise RepomixError(f"Repository clone failed: {error}") from error
