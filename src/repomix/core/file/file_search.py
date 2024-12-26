"""
File Search Module - Responsible for Searching and Filtering Files in the File System
"""

import fnmatch
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

from ...config.config_schema import RepomixConfig
from ...config.default_ignore import default_ignore_list
from ...shared.logger import logger


@dataclass
class FileSearchResult:
    """File Search Result

    Attributes:
        file_paths: List of found file paths
        empty_dir_paths: List of empty directory paths
    """

    file_paths: List[str]
    empty_dir_paths: List[str]


@dataclass
class PermissionError(Exception):
    """Permission Error Exception"""

    path: str
    message: str


@dataclass
class PermissionCheckResult:
    """Permission Check Result

    Attributes:
        has_permission: Whether permission is granted
        error: Error information if permission is not granted
    """

    has_permission: bool
    error: Optional[Exception] = None


def check_directory_permissions(directory: str | Path) -> PermissionCheckResult:
    """Check directory permissions

    Args:
        directory: Directory path

    Returns:
        Permission check result
    """
    try:
        path = Path(directory)
        list(path.iterdir())
        return PermissionCheckResult(has_permission=True)
    except PermissionError as e:
        return PermissionCheckResult(
            has_permission=False,
            error=PermissionError(path=str(directory), message=f"No permission to access directory: {e}"),
        )
    except Exception as e:
        return PermissionCheckResult(has_permission=False, error=e)


def find_empty_directories(root_dir: str | Path, directories: List[str], ignore_patterns: List[str]) -> List[str]:
    """Find empty directories

    Args:
        root_dir: Root directory
        directories: List of directories
        ignore_patterns: List of ignore patterns

    Returns:
        List of empty directory paths
    """
    empty_dirs: List[str] = []
    root_path = Path(root_dir)

    for dir_path in directories:
        full_path = root_path / dir_path
        try:
            has_visible_contents = any(not entry.name.startswith(".") for entry in full_path.iterdir())

            if not has_visible_contents:
                should_ignore = any(
                    dir_path == pattern or str(Path(pattern)) in str(Path(dir_path)).split("/")
                    for pattern in ignore_patterns
                )

                if not should_ignore:
                    empty_dirs.append(dir_path)
        except Exception as error:
            logger.debug(f"Error checking directory {dir_path}: {error}")

    return empty_dirs


def search_files(root_dir: str | Path, config: RepomixConfig) -> FileSearchResult:
    """Search files

    Args:
        root_dir: Root directory
        config: Configuration object

    Returns:
        File search result

    Raises:
        PermissionError: When insufficient permissions to access the directory
    """
    # Check directory permissions
    permission_check = check_directory_permissions(root_dir)
    if not permission_check.has_permission:
        if isinstance(permission_check.error, PermissionError):
            raise permission_check.error
        elif isinstance(permission_check.error, Exception):
            raise permission_check.error
        else:
            raise Exception("Unknown error")

    # Get filter rules
    ignore_patterns = get_ignore_patterns(root_dir, config)
    include_patterns = config.include if config.include else ["*"]

    root_path = Path(root_dir)
    all_files: List[str] = []
    all_dirs: List[str] = []

    for path in root_path.rglob("*"):
        rel_path = str(path.relative_to(root_path))

        # Modify ignore logic, place multiple conditions in a list for any judgment
        ignore_conditions = [
            fnmatch.fnmatch(rel_path, pattern)
            or fnmatch.fnmatch(rel_path, pattern.lstrip("/"))
            or fnmatch.fnmatch(rel_path, pattern.replace("**/", ""))
            or any(part == pattern.lstrip("/") for part in Path(rel_path).parts)
            for pattern in ignore_patterns
        ]
        should_ignore = any(ignore_conditions)

        if not should_ignore:
            if path.is_file():
                all_files.append(rel_path)
            elif path.is_dir():
                all_dirs.append(rel_path)

    # Filter files
    filtered_files = filter_paths(all_files, include_patterns, ignore_patterns)

    # Find empty directories
    empty_dirs = find_empty_directories(root_dir, all_dirs, ignore_patterns)

    return FileSearchResult(file_paths=filtered_files, empty_dir_paths=empty_dirs)


def get_ignore_patterns(root_dir: str | Path, config: RepomixConfig) -> List[str]:
    """Get list of ignore patterns

    Args:
        root_dir: Root directory
        config: Configuration object

    Returns:
        List of ignore patterns
    """
    patterns: List[str] = []

    # Add default ignore patterns
    if config.ignore.use_default_ignore:
        patterns.extend(default_ignore_list)

    # Add patterns from .gitignore
    if config.ignore.use_gitignore:
        gitignore_path = Path(root_dir) / ".gitignore"
        if gitignore_path.exists():
            try:
                patterns.extend(
                    line.strip()
                    for line in gitignore_path.read_text().splitlines()
                    if line.strip() and not line.startswith("#")
                )
            except Exception as error:
                logger.warn(f"Failed to read .gitignore file: {error}")

    # Add custom ignore patterns
    if config.ignore.custom_patterns:
        patterns.extend(config.ignore.custom_patterns)

    return patterns


def filter_paths(paths: List[str], include_patterns: List[str], ignore_patterns: List[str]) -> List[str]:
    """Filter file paths

    Args:
        paths: List of file paths
        include_patterns: List of include patterns
        ignore_patterns: List of ignore patterns

    Returns:
        List of filtered file paths
    """
    filtered_paths: List[str] = []

    for path in paths:
        # Check if it matches any include pattern
        is_included = any(fnmatch.fnmatch(path, pattern) for pattern in include_patterns)

        # Check if it matches any ignore pattern
        is_ignored = any(fnmatch.fnmatch(path, pattern) for pattern in ignore_patterns)

        if is_included and not is_ignored:
            filtered_paths.append(path)

    return filtered_paths
