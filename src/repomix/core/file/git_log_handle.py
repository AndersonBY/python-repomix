"""
Git Log Handle Module - Handles Git Log Operations
"""

from dataclasses import dataclass, field
from typing import List

from ...shared.logger import logger
from ...config.config_schema import RepomixConfig
from .git_command import exec_git_log, is_git_repository


# Null character used as record separator in git log output for robust parsing
# This ensures commits are split correctly even when commit messages contain newlines
GIT_LOG_RECORD_SEPARATOR = "\x00"

# Git format string for null character separator
# Git expects %x00 format in pretty format strings
GIT_LOG_FORMAT_SEPARATOR = "%x00"


@dataclass
class GitLogCommit:
    """Represents a single git commit"""

    date: str
    message: str
    files: List[str] = field(default_factory=list)


@dataclass
class GitLogResult:
    """Result of git log operations"""

    log_content: str
    commits: List[GitLogCommit] = field(default_factory=list)


def parse_git_log(raw_log_output: str, record_separator: str = GIT_LOG_RECORD_SEPARATOR) -> List[GitLogCommit]:
    """Parse raw git log output into structured commits

    Args:
        raw_log_output: Raw output from git log command
        record_separator: Separator used between commits

    Returns:
        List of GitLogCommit objects
    """
    if not raw_log_output.strip():
        return []

    commits: List[GitLogCommit] = []

    # Split by record separator used in git log output
    # This is more robust than splitting by double newlines, as commit messages may contain newlines
    log_entries = [entry for entry in raw_log_output.split(record_separator) if entry]

    for entry in log_entries:
        # Split on both \n and \r\n to handle different line ending formats across platforms
        lines = [line for line in entry.replace("\r\n", "\n").split("\n") if line.strip()]
        if not lines:
            continue

        # First line contains date and message separated by |
        first_line = lines[0]
        separator_index = first_line.find("|")
        if separator_index == -1:
            continue

        date = first_line[:separator_index]
        message = first_line[separator_index + 1 :]

        # Remaining lines are file paths
        files = [line.strip() for line in lines[1:] if line.strip()]

        commits.append(GitLogCommit(date=date, message=message, files=files))

    return commits


def get_git_log(directory: str, max_commits: int) -> str:
    """Get git log for a directory

    Args:
        directory: Repository directory
        max_commits: Maximum number of commits to retrieve

    Returns:
        Raw git log output string
    """
    if not is_git_repository(directory):
        logger.trace(f"Directory {directory} is not a git repository")
        return ""

    try:
        return exec_git_log(directory, max_commits, GIT_LOG_FORMAT_SEPARATOR)
    except Exception as e:
        logger.trace(f"Failed to get git log: {e}")
        raise


def get_git_logs(
    root_dirs: list,
    config: RepomixConfig,
) -> GitLogResult | None:
    """Get git logs if enabled in configuration

    Args:
        root_dirs: List of root directories
        config: Repomix configuration

    Returns:
        GitLogResult containing log content and parsed commits, or None if disabled
    """
    # Check if git logs are enabled
    if not config.output.git.include_logs:
        return None

    try:
        # Use the first directory as the git repository root
        git_root = root_dirs[0] if root_dirs else "."
        max_commits = config.output.git.include_logs_count

        log_content = get_git_log(git_root, max_commits)

        # Parse the raw log content into structured commits
        commits = parse_git_log(log_content)

        return GitLogResult(log_content=log_content, commits=commits)
    except Exception as e:
        logger.warn(f"Failed to get git logs: {e}")
        return None
