from pathlib import Path
from fnmatch import fnmatch
from dataclasses import dataclass
from typing import Dict, List, Union

import tiktoken

from ..config.config_load import load_config
from ..config.config_schema import RepomixConfig
from ..core.file.file_collect import collect_files
from ..core.file.file_process import process_files
from ..core.file.file_search import search_files, get_ignore_patterns
from ..core.output.output_generate import generate_output
from ..core.security.security_check import check_files, SuspiciousFileResult
from ..shared.error_handle import RepomixError
from ..shared.fs_utils import create_temp_directory, cleanup_temp_directory
from ..shared.git_utils import format_git_url, clone_repository


gpt_4o_encoding = tiktoken.encoding_for_model("gpt-4o")


def build_file_tree_with_ignore(directory: str | Path, config: RepomixConfig) -> Dict:
    """Builds a file tree, respecting ignore patterns."""
    ignore_patterns = get_ignore_patterns(directory, config)
    return _build_file_tree_recursive(Path(directory), ignore_patterns)


def _build_file_tree_recursive(directory: Path, ignore_patterns: List[str], base_dir: Path | None = None) -> Dict:
    """Recursive helper function for building the file tree."""
    tree = {}
    if base_dir is None:
        base_dir = directory

    for path in directory.iterdir():
        # Get path relative to the base directory for pattern matching
        rel_path = str(path.relative_to(base_dir))

        # Normalize path separators to forward slashes for consistent matching
        rel_path = rel_path.replace("\\", "/")

        # For directories, ensure path ends with / to match directory patterns
        if path.is_dir():
            rel_path_for_match = rel_path + "/"
        else:
            rel_path_for_match = rel_path

        if any(fnmatch(rel_path_for_match, pattern.replace("\\", "/")) for pattern in ignore_patterns):
            continue  # Skip ignored files/directories

        if path.is_dir():
            # Pass base_dir to maintain consistent relative paths
            subtree = _build_file_tree_recursive(path, ignore_patterns, base_dir)
            if subtree:  # Only add non-empty directories
                tree[path.name] = subtree
        else:
            tree[path.name] = ""
    return tree


@dataclass
class RepoProcessorResult:
    config: RepomixConfig
    file_tree: Dict[str, Union[str, List]]
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
        config: RepomixConfig | None = None,
        config_path: str | None = None,
        cli_options: Dict | None = None,
    ):
        if directory is None and repo_url is None:
            raise RepomixError("Either directory or repo_url must be provided")

        self.repo_url = repo_url
        self.temp_dir = None
        self.directory = directory
        self.config = config
        self.config_path = config_path
        self.cli_options = cli_options
        if self.config is None:
            if self.directory is None:
                _directory = Path.cwd()
            else:
                _directory = Path(self.directory)

            self.config = load_config(_directory, _directory, self.config_path, self.cli_options)

    def process(self, write_output: bool = True) -> RepoProcessorResult:
        """Process the code repository and return results."""
        try:
            if self.repo_url:
                self.temp_dir = create_temp_directory()
                clone_repository(format_git_url(self.repo_url), self.temp_dir)
                self.directory = self.temp_dir

            if self.config is None:
                raise RepomixError("Configuration not loaded.")

            if self.directory is None:
                raise RepomixError("Directory not set.")

            search_result = search_files(self.directory, self.config)
            raw_files = collect_files(search_result.file_paths, self.directory)

            if not raw_files:
                raise RepomixError("No files found. Please check the directory path and filter conditions.")

            # Build the file tree, considering ignore patterns
            file_tree = build_file_tree_with_ignore(self.directory, self.config)

            processed_files = process_files(raw_files, self.config)

            file_char_counts: Dict[str, int] = {}
            file_token_counts: Dict[str, int] = {}
            total_chars = 0
            total_tokens = 0

            for processed_file in processed_files:
                char_count = len(processed_file.content)
                token_count = len(gpt_4o_encoding.encode(processed_file.content))
                file_char_counts[processed_file.path] = char_count
                file_token_counts[processed_file.path] = token_count
                total_chars += char_count
                total_tokens += token_count

            suspicious_files_results = []
            if self.config.security.enable_security_check:
                file_contents = {file.path: file.content for file in raw_files}
                suspicious_files_results = check_files(self.directory, search_result.file_paths, file_contents)

            output_content = generate_output(
                processed_files, self.config, file_char_counts, file_token_counts, file_tree
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

    def write_output(self, output_content: str) -> None:
        """Write output content to file

        Args:
            output_content: Output content
        """
        if self.config is None:
            raise RepomixError("Configuration not loaded.")

        output_path = Path(self.config.output.file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_content, encoding="utf-8")
