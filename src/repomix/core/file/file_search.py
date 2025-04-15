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


def _should_ignore_path(path: str, ignore_patterns: List[str]) -> bool:
    """Check if the path should be ignored"""
    path = path.replace("\\", "/")  # Normalize to forward slashes

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

            # Check directory path match (ensure directory patterns match correctly)
            if pattern.endswith("/"):
                if fnmatch.fnmatch(current_path + "/", pattern):
                    return True

    return False


def _scan_directory(current_dir: Path, root_path: Path, all_files: List[str], all_dirs: List[str]) -> None:
    """Recursively scan directory without applying ignore patterns initially."""
    if current_dir.name == ".git" and current_dir.parent == root_path:
        logger.debug("Ignoring .git directory at root")
        return

    try:
        for entry in current_dir.iterdir():
            if ".git" in entry.parts:
                continue

            rel_path = str(entry.relative_to(root_path))

            if entry.is_file():
                all_files.append(rel_path)
            elif entry.is_dir():
                all_dirs.append(rel_path)
                _scan_directory(entry, root_path, all_files, all_dirs)
    except Exception as error:
        logger.debug(f"Error scanning directory {current_dir}: {error}")


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
    # 1. 检查权限 (保持不变)
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

    # 2. 完整扫描获取原始列表
    logger.debug("Starting raw directory scan...")
    _scan_directory(root_path, root_path, raw_all_files, raw_all_dirs)
    logger.debug(f"Raw scan found {len(raw_all_files)} files and {len(raw_all_dirs)} directories.")

    # 3. 获取 Include 和 Ignore 规则
    ignore_patterns = get_ignore_patterns(root_dir, config)
    include_patterns = config.include  # 获取 include 列表

    # 4. 应用 Include 规则 (如果 include 列表不为空)
    if include_patterns:
        logger.debug(f"Applying include patterns: {include_patterns}")
        potentially_included_files = []
        normalized_include_patterns = [p.replace("\\", "/") for p in include_patterns]

        for file_path in raw_all_files:
            normalized_path = file_path.replace("\\", "/")
            is_included = False
            for pattern in normalized_include_patterns:
                # 1. Direct fnmatch check (for file patterns like *.py or specific files)
                if fnmatch.fnmatch(normalized_path, pattern):
                    is_included = True
                    # logger.trace(f"Included '{normalized_path}' via fnmatch with pattern '{pattern}'")
                    break

                # 2. Directory check: if pattern ends with '/', check if path starts with it
                #    This handles patterns like "src/"
                if pattern.endswith("/") and normalized_path.startswith(pattern):
                    is_included = True
                    # logger.trace(f"Included '{normalized_path}' via startswith directory pattern '{pattern}'")
                    break

                # 3. Directory check: if pattern doesn't look like a file glob, treat as dir
                #    This handles patterns like "data" or "config" implicitly meaning "data/" or "config/"
                #    We check if the pattern itself contains wildcards typical for files at the end
                #    or doesn't contain a slash (implying a root level dir/file)
                #    A simple heuristic: if no typical file wildcards are present, assume directory.
                is_likely_dir_pattern = not any(c in pattern.split("/")[-1] for c in "*?")

                if is_likely_dir_pattern:
                    # Ensure directory patterns match from the start of the path segments
                    dir_prefix = pattern.rstrip("/") + "/"
                    if normalized_path.startswith(dir_prefix):
                        is_included = True
                        # logger.trace(f"Included '{normalized_path}' via implied directory pattern '{pattern}' (matching prefix '{dir_prefix}')")
                        break

            if is_included:
                potentially_included_files.append(file_path)
            # else:
            # logger.trace(f"Excluding '{normalized_path}' - did not match any include patterns.")

        logger.debug(f"{len(potentially_included_files)} files potentially included after include filter.")
    else:
        # 如果 include 为空，则所有文件都可能被包含 (等待 ignore 过滤)
        logger.debug("Include list is empty, considering all raw files initially.")
        potentially_included_files = raw_all_files

    # 5. 应用 Ignore 规则 (这部分代码保持不变)
    logger.debug(f"Applying ignore patterns: {ignore_patterns}")
    final_files: List[str] = []
    # *** Pass the root_path to _should_ignore_path for context ***
    for file_path in potentially_included_files:
        # 使用 _should_ignore_path 检查路径是否应被忽略
        # IMPORTANT: Make sure _should_ignore_path receives root_path if needed for relative checks
        # Assuming _should_ignore_path definition is:
        # def _should_ignore_path(path: str, ignore_patterns: List[str], root_path: Path) -> bool:
        # If not, adjust the call or the function signature.
        # For now, assuming the original _should_ignore_path doesn't need root_path explicitly passed here.
        # If it does, the call should be: if not _should_ignore_path(file_path, ignore_patterns, root_path):
        if not _should_ignore_path(file_path, ignore_patterns):  # Pass root_path if needed by the function
            final_files.append(file_path)
        # else:
        #     logger.trace(f"Ignoring file due to ignore patterns: {file_path}")
    logger.debug(f"{len(final_files)} files remaining after ignore filter.")

    # 5. 应用 Ignore 规则
    logger.debug(f"Applying ignore patterns: {ignore_patterns}")
    final_files: List[str] = []
    for file_path in potentially_included_files:
        # 使用 _should_ignore_path 检查路径是否应被忽略
        if not _should_ignore_path(file_path, ignore_patterns):
            final_files.append(file_path)
        # else:
        #     logger.trace(f"Ignoring file due to ignore patterns: {file_path}")
    logger.debug(f"{len(final_files)} files remaining after ignore filter.")

    # 6. 过滤目录列表以查找空目录 (也需要应用 ignore)
    final_dirs = [d for d in raw_all_dirs if not _should_ignore_path(d, ignore_patterns)]

    # 7. 查找空目录 (基于过滤后的目录列表)
    empty_dirs = find_empty_directories(root_dir, final_dirs, ignore_patterns)
    logger.debug(f"Found {len(empty_dirs)} empty directories to include (if configured).")

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
            new_patterns = [
                line.strip()
                for line in repomixignore_path.read_text().splitlines()
                if line.strip() and not line.startswith("#")
            ]
            patterns.extend(new_patterns)
        except Exception as error:
            logger.warn(f"Failed to read .repomixignore: {error}")

    # Add patterns from .gitignore
    if config.ignore.use_gitignore:
        gitignore_path = Path(root_dir) / ".gitignore"
        if gitignore_path.exists():
            try:
                new_patterns = [
                    line.strip()
                    for line in gitignore_path.read_text().splitlines()
                    if line.strip() and not line.startswith("#")
                ]
                patterns.extend(new_patterns)
            except Exception as error:
                logger.warn(f"Failed to read .gitignore file: {error}")

    # Add custom ignore patterns
    if config.ignore.custom_patterns:
        patterns.extend(config.ignore.custom_patterns)

    return patterns


def filter_paths(
    paths: List[str],
    include_patterns: List[str],
    ignore_patterns: List[str],
    base_dir: str | Path | None = None,
) -> List[str]:
    """Filter file paths

    Args:
        paths: List of file paths
        include_patterns: List of include patterns
        ignore_patterns: List of ignore patterns
        base_dir: Base directory for relative path calculation
    Returns:
        List of filtered file paths
    """
    filtered_paths: List[str] = []

    for path in paths:
        # Get relative path if base_dir is provided
        if base_dir:
            try:
                rel_path = str(Path(path).relative_to(Path(base_dir)))
            except ValueError:
                rel_path = path
        else:
            rel_path = path

        # Normalize path separators
        normalized_path = rel_path.replace("\\", "/")

        # Check if it matches any include pattern
        is_included = any(fnmatch.fnmatch(normalized_path, pattern.replace("\\", "/")) for pattern in include_patterns)

        # Check if path matches any ignore pattern (similar to _build_file_tree_recursive)
        is_ignored = any(
            fnmatch.fnmatch(normalized_path, pattern.replace("\\", "/"))
            or fnmatch.fnmatch(normalized_path + "/", pattern.replace("\\", "/"))
            or normalized_path.startswith(pattern.rstrip("/") + "/")
            for pattern in ignore_patterns
        )

        if is_included and not is_ignored:
            filtered_paths.append(path)

    return filtered_paths
