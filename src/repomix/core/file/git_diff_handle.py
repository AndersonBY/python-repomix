"""
Git Diff Handle Module - Handles Git Diff Operations
"""

from dataclasses import dataclass

from ...shared.logger import logger
from ...config.config_schema import RepomixConfig
from .git_command import exec_git_diff, is_git_repository


@dataclass
class GitDiffResult:
    """Result of git diff operations"""

    work_tree_diff_content: str
    staged_diff_content: str


def get_work_tree_diff(directory: str) -> str:
    """Get unstaged changes (working tree diff)

    Args:
        directory: Repository directory

    Returns:
        Git diff output for unstaged changes
    """
    return _get_diff(directory, [])


def get_staged_diff(directory: str) -> str:
    """Get staged changes (cached diff)

    Args:
        directory: Repository directory

    Returns:
        Git diff output for staged changes
    """
    return _get_diff(directory, ["--cached"])


def _get_diff(directory: str, options: list) -> str:
    """Helper function to get git diff with common repository check and error handling

    Args:
        directory: Repository directory
        options: Git diff options

    Returns:
        Git diff output string
    """
    try:
        # Check if the directory is a git repository
        if not is_git_repository(directory):
            logger.trace("Not a git repository, skipping diff generation")
            return ""

        # Get the diff with provided options
        result = exec_git_diff(directory, options)
        return result
    except Exception as e:
        logger.trace(f"Failed to get git diff: {e}")
        return ""


def get_git_diffs(
    root_dirs: list,
    config: RepomixConfig,
) -> GitDiffResult | None:
    """Get git diffs if enabled in configuration

    Args:
        root_dirs: List of root directories
        config: Repomix configuration

    Returns:
        GitDiffResult containing work tree and staged diffs, or None if disabled
    """
    # Check if git diffs are enabled
    if not config.output.git.include_diffs:
        return None

    try:
        # Use the first directory as the git repository root
        git_root = root_dirs[0] if root_dirs else "."

        work_tree_diff_content = get_work_tree_diff(git_root)
        staged_diff_content = get_staged_diff(git_root)

        return GitDiffResult(
            work_tree_diff_content=work_tree_diff_content,
            staged_diff_content=staged_diff_content,
        )
    except Exception as e:
        logger.warn(f"Failed to get git diffs: {e}")
        return None
