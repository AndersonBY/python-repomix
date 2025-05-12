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


def find_empty_directories(root_dir: str | Path, directories: List[str], ignore_patterns: List[str], config: Optional[RepomixConfig] = None) -> List[str]:
    """Find empty directories, respecting ignore patterns."""
    empty_dirs: List[str] = []
    root_path = Path(root_dir)

    for dir_path_str in directories:
        full_path = root_path / dir_path_str
        try:
            # Get all levels of .gitignore rules for the directory
            current_ignore_patterns = ignore_patterns.copy()
            if config and config.ignore.use_gitignore:
                local_patterns = collect_gitignore_patterns(full_path, root_path)
                if local_patterns:
                    current_ignore_patterns.extend(local_patterns)

            # Simplify: If the directory is empty, we check if it or its parent path matches the ignore rules
            is_empty = not any(full_path.iterdir())

            if is_empty:
                # Confirm that the empty directory itself or its path should be ignored
                current_dir = full_path if config else None
                if not _should_ignore_path(dir_path_str, current_ignore_patterns, current_dir, root_path):
                    empty_dirs.append(dir_path_str)
                # else:
                #    logger.trace(f"Empty directory {dir_path_str} ignored due to patterns.")

        except PermissionError:
            logger.warn(f"Permission denied checking directory {full_path}")
        except Exception as error:
            logger.debug(f"Error checking directory {dir_path_str}: {error}")

    return empty_dirs


def _should_ignore_path(path: str, ignore_patterns: List[str], current_dir: Optional[Path] = None, root_path: Optional[Path] = None) -> bool:
    """Check if the path should be ignored

    Args:
        path: The path to check (relative to the project root)
        ignore_patterns: The list of ignore patterns
        current_dir: The current directory being processed (for subdirectory .gitignore matching)
        root_path: The root path of the project
    """
    path = path.replace("\\", "/")  # Normalize to forward slashes

    # Process the path relative to the current directory (for subdirectory .gitignore rules)
    if current_dir is not None and root_path is not None:
        rel_to_current = None
        try:
            full_path = root_path / path
            if full_path.exists() and str(full_path).startswith(str(current_dir)):
                rel_to_current = str(full_path.relative_to(current_dir)).replace("\\", "/")
        except Exception:
            pass

    # Check if each part of the path should be ignored
    path_parts = Path(path).parts
    for i in range(len(path_parts)):
        current_path = str(Path(*path_parts[: i + 1])).replace("\\", "/")

        for pattern in ignore_patterns:
            pattern = pattern.replace("\\", "/")

            # Handle relative paths in patterns
            if pattern.startswith("./"):
                pattern = pattern[2:]
            if current_path.startswith("./"):
                current_path = current_path[2:]

            # Check full path match
            if fnmatch.fnmatch(current_path, pattern):
                return True

            # Check directory name match
            if fnmatch.fnmatch(path_parts[i], pattern):
                return True

            # Check if the last part of the path matches (handles ignores in subdirectories)
            if i == len(path_parts) - 1:
                last_part = path_parts[i]
                if fnmatch.fnmatch(last_part, pattern):
                    return True

            # Check directory path match (ensure directory patterns match correctly)
            if pattern.endswith("/"):
                if fnmatch.fnmatch(current_path + "/", pattern):
                    return True

                if i == len(path_parts) - 1 and fnmatch.fnmatch(path_parts[i] + "/", pattern):
                    return True

            # If there is a relative path to the current directory, check if it matches
            if current_dir is not None and root_path is not None and rel_to_current is not None:
                if pattern.endswith("/") and isinstance(rel_to_current, str):
                    if fnmatch.fnmatch(rel_to_current + "/", pattern):
                        return True
                if isinstance(rel_to_current, str) and fnmatch.fnmatch(rel_to_current, pattern):
                    return True

    return False


def _scan_directory(
    current_dir: Path,
    root_path: Path,
    all_files: List[str],
    all_dirs: List[str],
    ignore_patterns: List[str],
    config: Optional[RepomixConfig] = None,
) -> None:
    """Recursively scan directory, pruning ignored directories early."""
    is_root = current_dir == root_path
    if is_root:
        logger.debug(f"Scanning root directory: {current_dir}")

    # Process .git directory at root (common and efficient)
    if current_dir.name == ".git" and current_dir.parent == root_path:
        logger.debug("Ignoring .git directory at root")
        return

    # Check if there are single files specified in the configuration
    if config and config.include:
        for include_pattern in config.include:
            # Handle the case of single file
            if "*" not in include_pattern and "?" not in include_pattern and not include_pattern.endswith("/"):
                normalized_pattern = include_pattern.replace("\\", "/")
                file_path = root_path / normalized_pattern
                if file_path.exists() and file_path.is_file():
                    rel_path = file_path.relative_to(root_path).as_posix()
                    if is_root and rel_path not in all_files:
                        logger.debug(f"Found directly specified file from include pattern: {rel_path}")
                        all_files.append(rel_path)

    # Check if the current directory has a .gitignore file, and merge its rules
    current_ignore_patterns = ignore_patterns.copy()
    if config and config.ignore.use_gitignore:
        gitignore_path = current_dir / ".gitignore"
        if gitignore_path.exists() and gitignore_path != (root_path / ".gitignore"):
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    local_patterns = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
                    if local_patterns:
                        logger.debug(f"Found {len(local_patterns)} patterns in {gitignore_path}")
                        current_ignore_patterns.extend(local_patterns)
            except Exception as e:
                logger.warn(f"Failed to read local .gitignore file at {gitignore_path}: {e}")

    try:
        for entry in current_dir.iterdir():
            # Calculate the relative path (using as_posix to ensure '/' separator)
            try:
                rel_path = entry.relative_to(root_path).as_posix()
            except ValueError:
                # If entry is not under root_path (should not happen unless complex link cases)
                logger.warn(f"Entry {entry} seems outside root {root_path}, skipping.")
                continue

            # Pass current_dir parameter to support subdirectory .gitignore rules
            if _should_ignore_path(
                rel_path,
                current_ignore_patterns,
                current_dir if config else None,
                root_path,
            ):
                # logger.trace(f"Ignoring entry due to pattern match: {rel_path}")
                continue

            # If not ignored, continue processing
            if entry.is_file():
                all_files.append(rel_path)  # rel_path is already posix format
            elif entry.is_dir():
                # logger.trace(f"Entering directory: {rel_path}") # Optional trace
                all_dirs.append(rel_path)
                # Recursively call, passing current directory's ignore_patterns
                _scan_directory(entry, root_path, all_files, all_dirs, current_ignore_patterns, config)  # Pass current ignore patterns
    except PermissionError as e:
        logger.warn(f"Permission denied accessing directory {current_dir}: {e}")
    except Exception as error:
        # Record other possible scanning errors, such as path too long, but continue trying other entries
        logger.debug(f"Error scanning directory {current_dir}: {error}")


def search_files(root_dir: str | Path, config: RepomixConfig) -> FileSearchResult:
    """Search files, integrating ignore logic during scan.

    Args:
        root_dir: Root directory
        config: Configuration object

    Returns:
        File search result

    Raises:
        PermissionError: When insufficient permissions to access the directory
    """
    # 1.  permissions
    permission_check = check_directory_permissions(root_dir)
    if not permission_check.has_permission:
        if isinstance(permission_check.error, PermissionError):
            raise permission_check.error
        elif isinstance(permission_check.error, Exception):
            raise permission_check.error
        else:
            raise Exception("Unknown error")

    root_path = Path(root_dir)
    raw_all_files: List[str] = []
    raw_all_dirs: List[str] = []

    # 1.5 Preprocess single file paths in include patterns
    single_file_includes = []
    if config.include:
        for pattern in config.include:
            normalized_pattern = pattern.replace("\\", "/")
            # Check if it's a single file pattern (no wildcards and not ending with /)
            if "*" not in normalized_pattern and "?" not in normalized_pattern and not normalized_pattern.endswith("/"):
                file_path = root_path / normalized_pattern
                if file_path.exists() and file_path.is_file():
                    rel_path = file_path.relative_to(root_path).as_posix()
                    single_file_includes.append(rel_path)
                    logger.debug(f"Pre-processing: Found single file include: {rel_path}")

    # 2. Get root directory's ignore rules *before scanning*
    logger.debug("Calculating root ignore patterns...")
    root_ignore_patterns = get_ignore_patterns(root_dir, config)
    logger.debug(f"Using {len(root_ignore_patterns)} ignore patterns from root directory.")

    # 3. Execute directory scan with integrated ignore logic
    logger.debug("Starting directory scan with integrated ignore logic...")
    _scan_directory(root_path, root_path, raw_all_files, raw_all_dirs, root_ignore_patterns, config)  # Pass config
    logger.debug(f"Scan found {len(raw_all_files)} potentially relevant files and {len(raw_all_dirs)} directories.")

    # 4. Get include rules
    include_patterns = config.include

    # 5. Apply include rules
    if include_patterns:
        logger.debug(f"Applying include patterns: {include_patterns}")
        potentially_included_files = []
        # Note: include_patterns also need to normalize path separators, if they come from the config file
        normalized_include_patterns = [p.replace("\\", "/") for p in include_patterns]
        logger.debug(f"Normalized include patterns: {normalized_include_patterns}")

        for file_path in raw_all_files:
            # file_path comes from _scan_directory, already in posix format
            is_included = False
            logger.debug(f"Checking file: {file_path}")

            for pattern in normalized_include_patterns:
                # First check for exact file match, priority processing
                if file_path == pattern:
                    is_included = True
                    logger.debug(f"Exact file match: {file_path} matches pattern {pattern}")
                    break

                # Standard fnmatch wildcard matching
                if fnmatch.fnmatch(file_path, pattern):
                    is_included = True
                    logger.debug(f"Wildcard match: {file_path} matches pattern {pattern}")
                    break

                # Handle directory include pattern (ending with "/")
                if pattern.endswith("/") and file_path.startswith(pattern):
                    is_included = True
                    logger.debug(f"Directory prefix match: {file_path} in directory {pattern}")
                    break

                # Handle directory include pattern (not ending with "/")
                if not pattern.endswith("/") and "*" not in pattern and "?" not in pattern and file_path.startswith(pattern + "/"):
                    is_included = True
                    logger.debug(f"Implicit directory match: {file_path} in directory {pattern}/")
                    break

            if is_included:
                potentially_included_files.append(file_path)
                logger.debug(f"File included: {file_path}")
            else:
                logger.debug(f"File excluded: {file_path} (did not match any include patterns)")

        logger.debug(f"{len(potentially_included_files)} files potentially included after include filter.")
    else:
        logger.debug("Include list is empty, considering all scanned files.")
        potentially_included_files = raw_all_files

    # 6. Apply ignore rules again (final filter - lightweight)
    logger.debug("Applying final ignore filter...")
    final_files: List[str] = []

    # For each file, check if it should be ignored
    # Note: In _scan_directory, subdirectory .gitignore rules have already been considered, this is the final verification
    for file_path in potentially_included_files:
        full_path = root_path / file_path
        containing_dir = full_path.parent

        # Get all .gitignore rules from the directory containing the file and its parent directories
        current_ignore_patterns = root_ignore_patterns.copy()
        if config.ignore.use_gitignore:
            try:
                local_patterns = collect_gitignore_patterns(containing_dir, root_path)
                if local_patterns:
                    current_ignore_patterns.extend(local_patterns)
            except Exception as e:
                logger.debug(f"Error collecting local ignore patterns for {file_path}: {e}")

        # Check if the file should be ignored
        current_dir = containing_dir
        should_ignore = _should_ignore_path(file_path, current_ignore_patterns, current_dir, root_path)

        if should_ignore:
            logger.debug(f"Final filter: Ignoring file {file_path} due to ignore patterns")
        else:
            logger.debug(f"Final filter: Including file {file_path}")
            final_files.append(file_path)

    logger.debug(f"{len(final_files)} files remaining after final ignore filter.")

    # 7. Filter directory list
    final_dirs = []
    for dir_path in raw_all_dirs:
        full_dir_path = root_path / dir_path

        # Get all .gitignore rules from the directory and its parent directories
        dir_ignore_patterns = root_ignore_patterns.copy()
        if config.ignore.use_gitignore:
            try:
                local_patterns = collect_gitignore_patterns(full_dir_path.parent, root_path)
                if local_patterns:
                    dir_ignore_patterns.extend(local_patterns)
            except Exception as e:
                logger.debug(f"Error collecting local ignore patterns for directory {dir_path}: {e}")

        current_dir = full_dir_path.parent
        if not _should_ignore_path(dir_path, dir_ignore_patterns, current_dir, root_path):
            final_dirs.append(dir_path)

    # 8. Find empty directories (based on filtered directory list)
    empty_dirs = []
    if config.output.include_empty_directories:
        # Pass config to support subdirectory .gitignore rules
        empty_dirs = find_empty_directories(root_dir, final_dirs, root_ignore_patterns, config)
        logger.debug(f"Found {len(empty_dirs)} empty directories to include.")
    else:
        logger.debug("Empty directory inclusion is disabled.")

    # 9. Ensure single files are always included in the final result
    if single_file_includes:
        for file_path in single_file_includes:
            if file_path not in final_files:
                logger.debug(f"Ensuring single file include is in final result: {file_path}")
                final_files.append(file_path)

    return FileSearchResult(file_paths=final_files, empty_dir_paths=empty_dirs)


def get_ignore_patterns(root_dir: str | Path, config: RepomixConfig) -> List[str]:
    """Get list of ignore patterns"""
    patterns: List[str] = []

    # Add default ignore patterns
    if config.ignore.use_default_ignore:
        patterns.extend(default_ignore_list)

    repomixignore_path = Path(root_dir) / ".repomixignore"
    if repomixignore_path.exists():
        try:
            new_patterns = [line.strip() for line in repomixignore_path.read_text().splitlines() if line.strip() and not line.startswith("#")]
            patterns.extend(new_patterns)
        except Exception as error:
            logger.warn(f"Failed to read .repomixignore: {error}")

    # Add patterns from .gitignore
    if config.ignore.use_gitignore:
        gitignore_path = Path(root_dir) / ".gitignore"
        if gitignore_path.exists():
            try:
                new_patterns = [line.strip() for line in gitignore_path.read_text().splitlines() if line.strip() and not line.startswith("#")]
                patterns.extend(new_patterns)
            except Exception as error:
                logger.warn(f"Failed to read .gitignore file: {error}")

    # Add custom ignore patterns
    if config.ignore.custom_patterns:
        patterns.extend(config.ignore.custom_patterns)

    return patterns


def collect_gitignore_patterns(directory_path: Path, root_path: Path) -> List[str]:
    """Collect .gitignore rules from the specified directory and all its parent directories.

    Args:
        directory_path: The directory to start collecting .gitignore rules from
        root_path: The root path of the project (to stop the collection)

    Returns:
        List of ignore patterns from .gitignore files
    """
    patterns: List[str] = []

    # Start from the current directory and collect all parent directory's .gitignore rules
    current_dir = directory_path
    while str(current_dir).startswith(str(root_path)):
        gitignore_path = current_dir / ".gitignore"

        if gitignore_path.exists():
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    dir_patterns = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
                    patterns.extend(dir_patterns)
                    logger.debug(f"Added {len(dir_patterns)} patterns from {gitignore_path}")
            except Exception as e:
                logger.warn(f"Failed to read .gitignore file at {gitignore_path}: {e}")

        # If we've reached the project root, stop
        if current_dir == root_path:
            break

        # Move to the parent directory
        current_dir = current_dir.parent

    return patterns
