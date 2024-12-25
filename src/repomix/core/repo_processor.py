from pathlib import Path
from fnmatch import fnmatch
from dataclasses import dataclass
from typing import Dict, List, Union

import tiktoken

from ..config.config_schema import RepomixConfigMerged
from ..config.config_load import load_config
from ..core.file.file_collect import collect_files
from ..core.file.file_process import process_files
from ..core.file.file_search import search_files, get_ignore_patterns
from ..core.output.output_generate import generate_output
from ..core.security.security_check import check_files, SuspiciousFileResult
from ..shared.error_handle import RepomixError


gpt_4o_encoding = tiktoken.encoding_for_model("gpt-4o")


def build_file_tree(root_dir: str | Path) -> Dict[str, Union[str, List]]:
    """
    Builds a tree-like dictionary representing the file structure.

    Args:
        root_dir: The root directory to scan.

    Returns:
        A dictionary where keys are directory/file names and values are either
        strings (for files) or lists of dictionaries (for subdirectories).
    """
    root_path = Path(root_dir)
    tree = {}

    for path in root_path.iterdir():
        if path.is_dir():
            tree[path.name] = build_file_tree(path)
        else:
            tree[path.name] = ""  # Placeholder for file content, or leave empty if you just need the structure

    return tree


def build_file_tree_with_ignore(directory: str | Path, config: RepomixConfigMerged) -> Dict:
    """Builds a file tree, respecting ignore patterns."""
    ignore_patterns = get_ignore_patterns(directory, config)
    return _build_file_tree_recursive(Path(directory), ignore_patterns)


def _build_file_tree_recursive(directory: Path, ignore_patterns: List[str]) -> Dict:
    """Recursive helper function for building the file tree."""
    tree = {}
    for path in directory.iterdir():
        rel_path = str(path.relative_to(directory))
        if any(fnmatch(rel_path, pattern) for pattern in ignore_patterns):
            continue  # Skip ignored files/directories

        if path.is_dir():
            tree[path.name] = _build_file_tree_recursive(path, ignore_patterns)
        else:
            tree[path.name] = ""
    return tree


@dataclass
class RepoProcessorResult:
    config: RepomixConfigMerged
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
        directory: str | Path,
        config: RepomixConfigMerged | None = None,
        config_path: str | None = None,
        cli_options: Dict | None = None,
    ):
        self.directory = directory
        self.config = config
        self.config_path = config_path
        self.cli_options = cli_options
        if self.config is None:
            self.config = load_config(directory, directory, config_path, cli_options)

    def process(self) -> RepoProcessorResult:
        """Process the code repository and return results."""
        if self.config is None:
            raise RepomixError("Configuration not loaded.")

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

        output_content = generate_output(processed_files, self.config, file_char_counts, file_token_counts, file_tree)

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
