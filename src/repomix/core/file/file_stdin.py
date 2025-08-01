"""
Read file paths from stdin for processing.

This module provides functionality to read file paths from standard input,
one path per line, with support for comments and empty line filtering.
"""

import sys
from pathlib import Path
from typing import NamedTuple
from fnmatch import fnmatch

from repomix.shared.logger import logger
from repomix.config.default_ignore import default_ignore_list


class StdinFileResult(NamedTuple):
    """Result of reading file paths from stdin."""

    file_paths: list[str]
    empty_dir_paths: list[str]


def filter_valid_lines(lines: list[str]) -> list[str]:
    """
    Filter and validate lines from stdin input.

    Removes empty lines and comments (lines starting with #).

    Args:
        lines: Raw lines from stdin

    Returns:
        List of valid file paths
    """
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def should_ignore_path(file_path: Path) -> bool:
    """
    Check if a file path should be ignored based on default ignore patterns.

    Args:
        file_path: Path to check

    Returns:
        True if the path should be ignored, False otherwise
    """
    # Check each component of the path against ignore patterns
    for part in file_path.parts:
        for pattern in default_ignore_list:
            if fnmatch(part, pattern):
                return True

    # Check the full filename against patterns
    filename = file_path.name
    for pattern in default_ignore_list:
        if fnmatch(filename, pattern):
            return True

    return False


def resolve_and_deduplicate_paths(lines: list[str], cwd: Path) -> list[str]:
    """
    Resolve relative paths to absolute paths, filter ignored paths, and deduplicate them.

    Args:
        lines: List of file paths (relative or absolute)
        cwd: Current working directory

    Returns:
        List of unique absolute paths (excluding ignored paths)
    """
    filtered_paths = []
    ignored_count = 0

    for line in lines:
        path = Path(line)
        if path.is_absolute():
            file_path = path.resolve()
        else:
            file_path = (cwd / path).resolve()

        # Check if path should be ignored
        if should_ignore_path(file_path):
            logger.trace(f"Ignored path: {file_path}")
            ignored_count += 1
            continue

        logger.trace(f"Resolved path: {line} -> {file_path}")
        filtered_paths.append(str(file_path))

    if ignored_count > 0:
        logger.debug(f"Filtered out {ignored_count} paths based on ignore patterns")

    # Deduplicate while preserving order
    seen = set()
    unique_paths = []
    for path in filtered_paths:
        if path not in seen:
            seen.add(path)
            unique_paths.append(path)

    return unique_paths


async def read_file_paths_from_stdin(cwd: Path) -> StdinFileResult:
    """
    Read file paths from stdin, one per line.

    Filters out empty lines and comments (lines starting with #).
    Converts relative paths to absolute paths based on the current working directory.

    Args:
        cwd: Current working directory

    Returns:
        StdinFileResult containing file paths and empty directory paths

    Raises:
        ValueError: If stdin is a TTY or no valid paths are found
    """
    logger.trace("Reading file paths from stdin...")

    try:
        # Check if stdin is a TTY (interactive mode)
        if sys.stdin.isatty():
            raise ValueError("No data provided via stdin. Please pipe file paths to repomix when using --stdin flag.")

        # Read all lines from stdin
        raw_lines = sys.stdin.read().splitlines()

        # Filter out empty lines and comments
        valid_lines = filter_valid_lines(raw_lines)

        if not valid_lines:
            raise ValueError("No valid file paths found in stdin input.")

        # Convert relative paths to absolute paths and deduplicate
        file_paths = resolve_and_deduplicate_paths(valid_lines, cwd)

        logger.trace(f"Found {len(file_paths)} file paths from stdin")

        return StdinFileResult(
            file_paths=file_paths,
            empty_dir_paths=[],  # Empty directories not supported with stdin input
        )

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Failed to read file paths from stdin: {e}")
