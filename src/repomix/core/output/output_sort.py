"""
Output Sort Module - Sorts files by git change count
"""

from pathlib import Path
from typing import Dict, List

from ...shared.logger import logger
from ...config.config_schema import RepomixConfig
from ..file.file_types import ProcessedFile
from ..file.git_command import exec_git_log_filenames, is_git_installed


# Cache for git file change counts to avoid repeated git operations
# Key format: `{cwd}:{max_commits}`
_file_change_counts_cache: Dict[str, Dict[str, int]] = {}

# Cache for git availability check per cwd
_git_availability_cache: Dict[str, bool] = {}


def _build_cache_key(cwd: str, max_commits: int | None) -> str:
    """Build cache key for file change counts"""
    return f"{cwd}:{max_commits if max_commits else 'default'}"


def get_file_change_count(directory: str, max_commits: int = 100) -> Dict[str, int]:
    """Get file change counts from git log

    Args:
        directory: Repository directory
        max_commits: Maximum number of commits to check

    Returns:
        Dictionary mapping file paths to change counts
    """
    try:
        filenames = exec_git_log_filenames(directory, max_commits)

        file_change_counts: Dict[str, int] = {}
        for filename in filenames:
            file_change_counts[filename] = file_change_counts.get(filename, 0) + 1

        return file_change_counts
    except Exception as e:
        logger.trace(f"Failed to get file change counts: {e}")
        return {}


def _check_git_availability(cwd: str) -> bool:
    """Check if git is available in the given directory.
    Results are cached per cwd.

    Args:
        cwd: Working directory

    Returns:
        True if git is available, False otherwise
    """
    cached = _git_availability_cache.get(cwd)
    if cached is not None:
        return cached

    # Check if Git is installed
    if not is_git_installed():
        logger.trace("Git is not installed")
        _git_availability_cache[cwd] = False
        return False

    # Check if .git directory exists
    git_folder_path = Path(cwd) / ".git"
    if not git_folder_path.exists():
        logger.trace("Git folder not found")
        _git_availability_cache[cwd] = False
        return False

    _git_availability_cache[cwd] = True
    return True


def _get_file_change_counts(cwd: str, max_commits: int | None) -> Dict[str, int] | None:
    """Get file change counts from cache or git log.
    Returns None if git is not available or the command fails.

    Args:
        cwd: Working directory
        max_commits: Maximum number of commits to check

    Returns:
        Dictionary mapping file paths to change counts, or None if unavailable
    """
    cache_key = _build_cache_key(cwd, max_commits)

    # Check cache first
    cached = _file_change_counts_cache.get(cache_key)
    if cached is not None:
        logger.trace("Using cached git file change counts")
        return cached

    # Check git availability (cached per cwd)
    if not _check_git_availability(cwd):
        return None

    # Fetch from git log
    try:
        file_change_counts = get_file_change_count(cwd, max_commits or 100)
        _file_change_counts_cache[cache_key] = file_change_counts

        sorted_counts = sorted(file_change_counts.items(), key=lambda x: x[1], reverse=True)
        logger.trace(f"Git File change counts max commits: {max_commits}")
        logger.trace(f"Git File change counts: {sorted_counts[:10]}...")  # Log top 10

        return file_change_counts
    except Exception:
        return None


def _sort_files_by_change_counts(files: List[ProcessedFile], file_change_counts: Dict[str, int]) -> List[ProcessedFile]:
    """Sort files by change count (files with more changes go to the bottom)

    Args:
        files: List of processed files
        file_change_counts: Dictionary mapping file paths to change counts

    Returns:
        Sorted list of processed files
    """
    return sorted(files, key=lambda f: file_change_counts.get(f.path, 0))


def sort_output_files(
    files: List[ProcessedFile],
    config: RepomixConfig,
) -> List[ProcessedFile]:
    """Sort files by git change count for output

    Args:
        files: List of processed files
        config: Repomix configuration

    Returns:
        Sorted list of processed files
    """
    if not config.output.git.sort_by_changes:
        logger.trace("Git sort is not enabled")
        return files

    cwd = config.cwd or "."
    file_change_counts = _get_file_change_counts(cwd, config.output.git.sort_by_changes_max_commits)

    if not file_change_counts:
        return files

    return _sort_files_by_change_counts(files, file_change_counts)


def clear_caches() -> None:
    """Clear all caches (useful for testing)"""
    global _file_change_counts_cache, _git_availability_cache
    _file_change_counts_cache = {}
    _git_availability_cache = {}
