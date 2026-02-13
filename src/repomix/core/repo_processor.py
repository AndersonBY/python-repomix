from pathlib import Path
from fnmatch import fnmatch
from dataclasses import dataclass
from typing import Dict, List, Any, Sequence
import re
import logging
from functools import lru_cache


from ..config.config_load import load_config
from ..config.config_schema import RepomixConfig
from ..core.file.file_collect import collect_files
from ..core.file.file_types import RawFile
from ..core.file.file_process import process_files
from ..core.file.file_search import search_files, get_ignore_patterns
from ..core.output.output_generate import generate_output
from ..core.security.security_check import check_files, SuspiciousFileResult
from ..shared.error_handle import RepomixError
from ..shared.fs_utils import create_temp_directory, cleanup_temp_directory
from ..shared.git_utils import format_git_url, clone_repository

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1000)
def cached_fnmatch(filename: str, pattern: str) -> bool:
    """Cached version of fnmatch for better performance."""
    try:
        return fnmatch(filename, pattern)
    except (re.error, OverflowError, RecursionError):
        return False


def build_full_file_tree(directory: str | Path) -> Dict:
    """Build a complete file tree without any filtering.

    This function builds a full directory tree including all files and directories,
    regardless of ignore patterns. Used when include_full_directory_structure is enabled.

    Args:
        directory: Root directory to scan

    Returns:
        Dictionary representing the complete file tree
    """
    return _build_full_tree_recursive(Path(directory))


def _build_full_tree_recursive(directory: Path, base_dir: Path | None = None) -> Dict:
    """Recursively build full file tree without filtering."""
    tree: Dict[str, Any] = {}
    if base_dir is None:
        base_dir = directory

    try:
        entries = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except (OSError, PermissionError):
        return tree

    for path in entries:
        try:
            path_name = path.name
            is_dir = path.is_dir()

            if is_dir:
                # Recursively build subtree for all directories
                subtree = _build_full_tree_recursive(path, base_dir)
                tree[path_name] = subtree if subtree else {}
            else:
                tree[path_name] = ""
        except Exception as e:
            logger.debug(f"Error processing path '{path}': {e}")
            continue

    return tree


def build_file_tree_with_ignore(directory: str | Path, config: RepomixConfig) -> Dict:
    """Builds a file tree, respecting ignore patterns - HEAVILY OPTIMIZED for large projects."""
    ignore_patterns = get_ignore_patterns(directory, config)

    # OPTIMIZATION: Pre-compile common ignore patterns for faster matching
    common_ignores = {
        "node_modules",
        ".git",
        "__pycache__",
        ".pytest_cache",
        "venv",
        ".venv",
        "env",
        ".env",
        "build",
        "dist",
        ".idea",
        ".vscode",
        "logs",
        "tmp",
        "cache",
    }

    # Separate patterns by type for faster processing
    dir_exact_matches = set()  # Exact directory names to ignore
    dir_patterns = []  # Pattern-based directory ignores
    file_patterns = []  # File-specific patterns

    for pattern in ignore_patterns:
        pattern = pattern.replace("\\", "/").strip()
        if not pattern:
            continue

        # Handle exact directory matches (fastest)
        if "/" not in pattern and "*" not in pattern and "[" not in pattern:
            dir_exact_matches.add(pattern)
        elif pattern.endswith("/"):
            clean_pattern = pattern[:-1]
            if "/" not in clean_pattern and "*" not in clean_pattern and "[" not in clean_pattern:
                dir_exact_matches.add(clean_pattern)
            else:
                dir_patterns.append(clean_pattern)
        else:
            file_patterns.append(pattern)
            # Also check as directory pattern
            dir_patterns.append(pattern)

    # Add common ignores to exact matches for super fast filtering
    dir_exact_matches.update(common_ignores)

    return _build_file_tree_super_optimized(Path(directory), dir_exact_matches, dir_patterns, file_patterns)


def _build_file_tree_super_optimized(
    directory: Path,
    dir_exact_matches: set,
    dir_patterns: List[str],
    file_patterns: List[str],
    base_dir: Path | None = None,
) -> Dict:
    """Super optimized recursive file tree builder with aggressive pruning."""
    tree = {}
    if base_dir is None:
        base_dir = directory

    try:
        entries = list(directory.iterdir())
    except (OSError, PermissionError):
        return tree

    for path in entries:
        try:
            path_name = path.name
            is_dir = path.is_dir()

            if is_dir:
                # SUPER OPTIMIZATION 1: Check exact matches first (O(1) lookup)
                if path_name in dir_exact_matches:
                    continue  # Skip immediately - no need to even calculate relative path

                # SUPER OPTIMIZATION 2: Early skip for hidden/temp directories
                if path_name.startswith(".") and path_name in {
                    ".git",
                    ".svn",
                    ".hg",
                    ".cache",
                }:
                    continue

                # Only calculate relative path if needed for pattern matching
                rel_path = path.relative_to(base_dir).as_posix()

                # Check directory patterns
                should_ignore_dir = False
                for pattern in dir_patterns:
                    if cached_fnmatch(rel_path, pattern):
                        should_ignore_dir = True
                        break

                if should_ignore_dir:
                    continue

                # Recursively build subtree
                subtree = _build_file_tree_super_optimized(path, dir_exact_matches, dir_patterns, file_patterns, base_dir)
                if subtree:
                    tree[path_name] = subtree
            else:
                # SUPER OPTIMIZATION 3: Quick file extension checks
                if path_name.endswith((".pyc", ".pyo", ".class", ".o", ".so", ".dll")):
                    continue  # Skip compiled files immediately

                # Only check file patterns if needed
                if file_patterns:
                    rel_path = path.relative_to(base_dir).as_posix()
                    should_ignore_file = False
                    for pattern in file_patterns:
                        if cached_fnmatch(rel_path, pattern):
                            should_ignore_file = True
                            break

                    if not should_ignore_file:
                        tree[path_name] = ""
                else:
                    tree[path_name] = ""

        except Exception as e:
            logger.debug(f"Error processing path '{path}': {e}")
            continue

    return tree


@dataclass
class RepoProcessorResult:
    config: RepomixConfig
    file_tree: Dict[str, str | List]
    total_files: int
    total_chars: int
    total_tokens: int
    file_char_counts: Dict[str, int]
    file_token_counts: Dict[str, int]
    output_content: str
    suspicious_files_results: List[SuspiciousFileResult]


class RepoProcessor:
    def __init__(
        self,
        directory: str | Path | None = None,
        repo_url: str | None = None,
        branch: str | None = None,
        config: RepomixConfig | None = None,
        config_path: str | None = None,
        cli_options: Dict | None = None,
        directories: Sequence[str | Path] | None = None,
    ):
        if directory is None and repo_url is None and directories is None:
            raise RepomixError("Either directory, directories, or repo_url must be provided")

        self.repo_url = repo_url
        self.temp_dir = None
        self.branch = branch
        self.config = config
        self.config_path = config_path
        self.cli_options = cli_options
        self._predefined_file_paths: List[str] | None = None  # For stdin mode

        # Normalize directories
        if directories is not None:
            self.directories = [str(d) for d in directories]
            self.directory = self.directories[0] if self.directories else None
        elif directory is not None:
            self.directory = directory
            self.directories = [str(directory)]
        else:
            self.directory = None
            self.directories = []

        if self.config is None:
            if self.directory is None:
                _directory = Path.cwd()
            else:
                _directory = Path(self.directory)

            self.config = load_config(_directory, _directory, self.config_path, self.cli_options)

    def set_predefined_file_paths(self, file_paths: List[str]) -> None:
        """Set predefined file paths for stdin mode.

        Args:
            file_paths: List of absolute file paths to process
        """
        self._predefined_file_paths = file_paths

    def process(self, write_output: bool = True) -> RepoProcessorResult:
        """Process the code repository and return results."""
        if self.config and self.config.output.calculate_tokens:
            import tiktoken

            encoding_name = getattr(self.config, 'token_count', None)
            encoding_name = encoding_name.encoding if encoding_name else "o200k_base"
            try:
                token_encoding = tiktoken.get_encoding(encoding_name)
            except Exception:
                logger.warning(f"Unknown encoding '{encoding_name}', falling back to o200k_base")
                token_encoding = tiktoken.get_encoding("o200k_base")
        else:
            token_encoding = None

        try:
            if self.repo_url:
                self.temp_dir = create_temp_directory()
                clone_repository(format_git_url(self.repo_url), self.temp_dir, self.branch)
                self.directory = self.temp_dir
                self.directories = [self.temp_dir]

            if self.config is None:
                raise RepomixError("Configuration not loaded.")

            if not self.directories:
                raise RepomixError("Directory not set.")

            is_multi_root = len(self.directories) > 1

            # Use predefined file paths if available (stdin mode)
            if self._predefined_file_paths is not None:
                # Convert absolute paths to relative paths based on directory
                dir_path = Path(self.directories[0]).resolve()
                relative_paths = []
                for abs_path in self._predefined_file_paths:
                    try:
                        rel_path = Path(abs_path).relative_to(dir_path)
                        relative_paths.append(str(rel_path))
                    except ValueError:
                        relative_paths.append(abs_path)

                raw_files = collect_files(relative_paths, self.directories[0])
                file_tree = self._build_tree_for_directory(self.directories[0])
            elif is_multi_root:
                # Multi-directory processing
                raw_files, file_tree = self._process_multiple_directories()
            else:
                # Single directory processing
                search_result = search_files(self.directories[0], self.config)
                raw_files = collect_files(search_result.file_paths, self.directories[0])
                file_tree = self._build_tree_for_directory(self.directories[0])

            if not raw_files:
                raise RepomixError("No files found. Please check the directory path and filter conditions.")

            processed_files = process_files(raw_files, self.config)

            file_char_counts: Dict[str, int] = {}
            file_token_counts: Dict[str, int] = {}
            total_chars = 0
            total_tokens = 0

            # Optimize character and token counting
            if self.config.output.calculate_tokens and token_encoding:
                for processed_file in processed_files:
                    char_count = len(processed_file.content)
                    file_char_counts[processed_file.path] = char_count
                    total_chars += char_count
                    try:
                        token_count = len(token_encoding.encode(processed_file.content))
                        file_token_counts[processed_file.path] = token_count
                        total_tokens += token_count
                    except Exception as e:
                        logger.debug(f"Token calculation failed for {processed_file.path}: {e}")
                        file_token_counts[processed_file.path] = 0
            else:
                for processed_file in processed_files:
                    char_count = len(processed_file.content)
                    file_char_counts[processed_file.path] = char_count
                    file_token_counts[processed_file.path] = 0
                    total_chars += char_count

            suspicious_files_results = []
            if self.config.security.enable_security_check:
                file_contents = {file.path: file.content for file in raw_files}
                file_paths = [file.path for file in raw_files]
                # Use first directory for security check base path
                suspicious_files_results = check_files(self.directories[0], file_paths, file_contents)
                suspicious_file_paths = {result.file_path for result in suspicious_files_results}
                processed_files = [file for file in processed_files if file.path not in suspicious_file_paths]

            output_content = generate_output(
                processed_files,
                self.config,
                file_char_counts,
                file_token_counts,
                file_tree,
            )

            if write_output:
                self.write_output(output_content)

            return RepoProcessorResult(
                config=self.config,
                file_tree=file_tree,
                total_files=len(processed_files),
                total_chars=total_chars,
                total_tokens=total_tokens,
                file_char_counts=file_char_counts,
                file_token_counts=file_token_counts,
                output_content=output_content,
                suspicious_files_results=suspicious_files_results,
            )

        finally:
            if self.temp_dir:
                cleanup_temp_directory(self.temp_dir)

    def _build_tree_for_directory(self, directory: str | Path) -> Dict:
        """Build file tree for a single directory based on config."""
        assert self.config is not None
        if self.config.output.include_full_directory_structure:
            return build_full_file_tree(directory)
        else:
            return build_file_tree_with_ignore(directory, self.config)

    def _process_multiple_directories(self):
        """Process multiple directories and merge results.

        Returns:
            Tuple of (merged raw_files, merged file_tree)
        """
        assert self.config is not None
        all_raw_files = []
        merged_tree: Dict[str, Any] = {}

        for directory in self.directories:
            dir_path = Path(directory).resolve()
            root_label = dir_path.name or str(dir_path)

            # Search and collect files for this directory
            search_result = search_files(directory, self.config)
            dir_raw_files = collect_files(search_result.file_paths, directory)

            # Prefix file paths with root label for multi-root
            for raw_file in dir_raw_files:
                prefixed_path = f"{root_label}/{raw_file.path}"
                all_raw_files.append(RawFile(path=prefixed_path, content=raw_file.content))

            # Build tree for this directory and nest under root label
            dir_tree = self._build_tree_for_directory(directory)
            merged_tree[root_label] = dir_tree

        return all_raw_files, merged_tree

    def write_output(self, output_content: str) -> None:
        """Write output content to file or stdout

        Args:
            output_content: Output content
        """
        if self.config is None:
            raise RepomixError("Configuration not loaded.")

        # If stdout is enabled, print to stdout instead of writing to file
        if self.config.output.stdout:
            print(output_content)
        else:
            output_path = Path(self.config.output.file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output_content, encoding="utf-8")
