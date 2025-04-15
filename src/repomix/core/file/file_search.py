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
    """Find empty directories, respecting ignore patterns."""
    empty_dirs: List[str] = []
    root_path = Path(root_dir)

    for dir_path_str in directories:  # dir_path_str 已经是相对posix路径
        full_path = root_path / dir_path_str
        try:
            # 简化：如果目录为空，我们再检查它或其父路径是否匹配忽略规则
            is_empty = not any(full_path.iterdir())

            if is_empty:
                # 再次确认这个空目录本身或其路径是否应被忽略
                if not _should_ignore_path(dir_path_str, ignore_patterns):
                    empty_dirs.append(dir_path_str)
                # else:
                #    logger.trace(f"Empty directory {dir_path_str} ignored due to patterns.")

        except PermissionError:
            logger.warn(f"Permission denied checking directory {full_path}")
        except Exception as error:
            logger.debug(f"Error checking directory {dir_path_str}: {error}")

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


def _scan_directory(
    current_dir: Path,
    root_path: Path,
    all_files: List[str],
    all_dirs: List[str],
    ignore_patterns: List[str],
) -> None:
    """Recursively scan directory, pruning ignored directories early."""
    # 优先处理根目录下的 .git (常见且高效)
    if current_dir.name == ".git" and current_dir.parent == root_path:
        logger.debug("Ignoring .git directory at root")
        return

    try:
        for entry in current_dir.iterdir():
            # 计算相对路径 (使用 as_posix 保证 '/' 分隔符)
            try:
                rel_path = entry.relative_to(root_path).as_posix()
            except ValueError:
                # 如果 entry 不在 root_path 下 (理论上不应发生，除非链接等复杂情况)
                logger.warn(f"Entry {entry} seems outside root {root_path}, skipping.")
                continue

            # === 核心改动：在处理前检查忽略规则 ===
            if _should_ignore_path(rel_path, ignore_patterns):
                # logger.trace(f"Ignoring entry due to pattern match: {rel_path}")
                continue
            # =====================================

            # 如果没有被忽略，则继续处理
            if entry.is_file():
                all_files.append(rel_path)  # rel_path 已经是 posix 格式
            elif entry.is_dir():
                # logger.trace(f"Entering directory: {rel_path}") # Optional trace
                all_dirs.append(rel_path)  # rel_path 已经是 posix 格式
                # 递归调用，传递 ignore_patterns
                _scan_directory(entry, root_path, all_files, all_dirs, ignore_patterns)  # 传递忽略模式
    except PermissionError as e:
        logger.warn(f"Permission denied accessing directory {current_dir}: {e}")
    except Exception as error:
        # 记录其他可能的扫描错误，例如路径太长等，但继续尝试其他条目
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

    # 2. 获取 Ignore 规则 *在扫描之前*
    logger.debug("Calculating ignore patterns...")
    ignore_patterns = get_ignore_patterns(root_dir, config)
    logger.debug(f"Using {len(ignore_patterns)} ignore patterns.")

    # 3. 执行带有忽略逻辑的扫描
    logger.debug("Starting directory scan with integrated ignore logic...")
    _scan_directory(root_path, root_path, raw_all_files, raw_all_dirs, ignore_patterns)  # 传递 ignore_patterns
    logger.debug(f"Scan found {len(raw_all_files)} potentially relevant files and {len(raw_all_dirs)} directories.")

    # 4. 获取 Include 规则
    include_patterns = config.include

    # 5. 应用 Include 规则
    if include_patterns:
        logger.debug(f"Applying include patterns: {include_patterns}")
        potentially_included_files = []
        # 注意：include_patterns 也需要规范化处理路径分隔符，如果它们来自配置文件
        normalized_include_patterns = [p.replace("\\", "/") for p in include_patterns]

        for file_path in raw_all_files:
            # file_path 来自 _scan_directory，已经是 posix 格式
            is_included = False
            for pattern in normalized_include_patterns:
                # 简化 include 匹配逻辑示例 (可能需要根据实际需求调整)
                # fnmatch 对 posix 路径有效
                if fnmatch.fnmatch(file_path, pattern):
                    is_included = True
                    break
                # 处理目录 include (例如 "src/")
                if pattern.endswith("/") and file_path.startswith(pattern):
                    is_included = True
                    break
                # 处理目录 include (例如 "src" 意为 "src/")
                if (
                    not pattern.endswith("/")
                    and "*" not in pattern
                    and "?" not in pattern
                    and file_path.startswith(pattern + "/")
                ):
                    is_included = True
                    break

            if is_included:
                potentially_included_files.append(file_path)

        logger.debug(f"{len(potentially_included_files)} files potentially included after include filter.")
    else:
        logger.debug("Include list is empty, considering all scanned files.")
        potentially_included_files = raw_all_files

    # 6. 应用 Ignore 规则 (第二次过滤 - 轻量级)
    # 这一步仍然需要，用于处理文件级忽略（如 *.log）以及可能被 include 覆盖的情况
    logger.debug("Applying final ignore filter (for file-specific patterns)...")
    final_files: List[str] = []
    # 假设 _should_ignore_path 内部处理好了路径规范化
    for file_path in potentially_included_files:
        if not _should_ignore_path(file_path, ignore_patterns):
            final_files.append(file_path)
        # else:
        #     logger.trace(f"Ignoring file due to final ignore check: {file_path}")
    logger.debug(f"{len(final_files)} files remaining after final ignore filter.")

    # 7. 过滤目录列表 (基于原始扫描结果，也需要应用ignore)
    # raw_all_dirs 已经是被初步过滤（忽略目录）的结果
    # 但仍需检查是否有目录本身被文件级模式忽略（虽然不常见，但可能）
    # 或者检查其父目录是否在 include 规则中被排除（更复杂）
    # 为了简化，我们直接使用 raw_all_dirs 作为基础，find_empty_directories 内部会再次检查
    # 但更好的做法是确保 raw_all_dirs 本身是正确的最终候选目录列表
    final_dirs = [d for d in raw_all_dirs if not _should_ignore_path(d, ignore_patterns)]

    # 8. 查找空目录 (基于过滤后的目录列表)
    empty_dirs = []
    if config.output.include_empty_directories:
        # 注意：find_empty_directories 也需要知道 ignore_patterns
        empty_dirs = find_empty_directories(root_dir, final_dirs, ignore_patterns)
        logger.debug(f"Found {len(empty_dirs)} empty directories to include.")
    else:
        logger.debug("Empty directory inclusion is disabled.")

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
