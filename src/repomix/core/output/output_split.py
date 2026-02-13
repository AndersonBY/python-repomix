"""
Output Split Module - Splits output into multiple parts based on size
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Callable, Any

from ...shared.logger import logger
from ...config.config_schema import RepomixConfig
from ..file.file_types import ProcessedFile


@dataclass
class OutputSplitGroup:
    """Group of files sharing the same root entry"""

    root_entry: str
    processed_files: List[ProcessedFile] = field(default_factory=list)
    all_file_paths: List[str] = field(default_factory=list)


@dataclass
class OutputSplitPart:
    """A single part of split output"""

    index: int
    file_path: str
    content: str
    byte_length: int
    groups: List[OutputSplitGroup] = field(default_factory=list)


def get_root_entry(relative_file_path: str) -> str:
    """Get the root entry (first directory or file) from a path

    Args:
        relative_file_path: Relative file path

    Returns:
        Root entry name
    """
    # Normalize path separators
    normalized = relative_file_path.replace("\\", "/")
    parts = normalized.split("/")
    return parts[0] if parts else normalized


def build_output_split_groups(processed_files: List[ProcessedFile], all_file_paths: List[str]) -> List[OutputSplitGroup]:
    """Build groups of files by their root entry

    Args:
        processed_files: List of processed files
        all_file_paths: List of all file paths

    Returns:
        List of OutputSplitGroup sorted by root entry
    """
    groups_by_root: dict[str, OutputSplitGroup] = {}

    # Group all file paths by root entry
    for file_path in all_file_paths:
        root_entry = get_root_entry(file_path)
        if root_entry not in groups_by_root:
            groups_by_root[root_entry] = OutputSplitGroup(root_entry=root_entry)
        groups_by_root[root_entry].all_file_paths.append(file_path)

    # Add processed files to their groups
    for processed_file in processed_files:
        root_entry = get_root_entry(processed_file.path)
        if root_entry not in groups_by_root:
            groups_by_root[root_entry] = OutputSplitGroup(root_entry=root_entry, all_file_paths=[processed_file.path])
        groups_by_root[root_entry].processed_files.append(processed_file)

    # Sort by root entry and return
    return sorted(groups_by_root.values(), key=lambda g: g.root_entry)


def build_split_output_file_path(base_file_path: str, part_index: int) -> str:
    """Build file path for a split output part

    Args:
        base_file_path: Base output file path
        part_index: Part index (1-based)

    Returns:
        File path for the part
    """
    path_obj = Path(base_file_path)
    ext = path_obj.suffix
    if not ext:
        return f"{base_file_path}.{part_index}"
    base_without_ext = str(path_obj.with_suffix(""))
    return f"{base_without_ext}.{part_index}{ext}"


def get_utf8_byte_length(content: str) -> int:
    """Get UTF-8 byte length of a string

    Args:
        content: String content

    Returns:
        Byte length in UTF-8 encoding
    """
    return len(content.encode("utf-8"))


def make_chunk_config(base_config: RepomixConfig, part_index: int) -> RepomixConfig:
    """Create config for a chunk, disabling git diffs/logs for non-first chunks

    Args:
        base_config: Base configuration
        part_index: Part index (1-based)

    Returns:
        Configuration for the chunk
    """
    if part_index == 1:
        return base_config

    # For non-first chunks, disable git diffs/logs to avoid repeating large sections
    import copy

    chunk_config = copy.deepcopy(base_config)
    chunk_config.output.git.include_diffs = False
    chunk_config.output.git.include_logs = False
    return chunk_config


def generate_split_output_parts(
    processed_files: List[ProcessedFile],
    all_file_paths: List[str],
    max_bytes_per_part: int,
    base_config: RepomixConfig,
    generate_output_fn: Callable[..., str],
    file_char_counts: dict[str, int],
    file_token_counts: dict[str, int],
    git_diff_result: Any | None = None,
    git_log_result: Any | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> List[OutputSplitPart]:
    """Generate split output parts

    Args:
        processed_files: List of processed files
        all_file_paths: List of all file paths
        max_bytes_per_part: Maximum bytes per output part
        base_config: Base configuration
        generate_output_fn: Function to generate output
        file_char_counts: Character counts per file
        file_token_counts: Token counts per file
        git_diff_result: Git diff result (optional)
        git_log_result: Git log result (optional)
        progress_callback: Progress callback function (optional)

    Returns:
        List of OutputSplitPart

    Raises:
        ValueError: If max_bytes_per_part is invalid or a single group exceeds the limit
    """
    if max_bytes_per_part <= 0:
        raise ValueError(f"Invalid max_bytes_per_part: {max_bytes_per_part}")

    groups = build_output_split_groups(processed_files, all_file_paths)
    if not groups:
        return []

    def report_progress(message: str) -> None:
        if progress_callback:
            progress_callback(message)
        logger.trace(message)

    def render_groups(groups_to_render: List[OutputSplitGroup], part_index: int) -> str:
        """Render a list of groups into output content"""
        chunk_processed_files = []
        for g in groups_to_render:
            chunk_processed_files.extend(g.processed_files)

        chunk_config = make_chunk_config(base_config, part_index)

        # Build file tree from groups
        from .output_generate import build_filtered_file_tree

        file_tree = build_filtered_file_tree(chunk_processed_files)

        return generate_output_fn(
            chunk_processed_files,
            chunk_config,
            file_char_counts,
            file_token_counts,
            file_tree,
            git_diff_result if part_index == 1 else None,
            git_log_result if part_index == 1 else None,
        )

    parts: List[OutputSplitPart] = []
    current_groups: List[OutputSplitGroup] = []
    current_content = ""
    current_bytes = 0

    for group in groups:
        part_index = len(parts) + 1
        next_groups = current_groups + [group]
        report_progress(f"Generating output... (part {part_index}) evaluating {group.root_entry}")

        next_content = render_groups(next_groups, part_index)
        next_bytes = get_utf8_byte_length(next_content)

        if next_bytes <= max_bytes_per_part:
            current_groups = next_groups
            current_content = next_content
            current_bytes = next_bytes
            continue

        if not current_groups:
            raise ValueError(
                f"Cannot split output: root entry '{group.root_entry}' exceeds max size. Part size {next_bytes:,} bytes > limit {max_bytes_per_part:,} bytes."
            )

        # Finalize current part and start a new one
        parts.append(
            OutputSplitPart(
                index=part_index,
                file_path=build_split_output_file_path(base_config.output.file_path, part_index),
                content=current_content,
                byte_length=current_bytes,
                groups=current_groups,
            )
        )

        new_part_index = len(parts) + 1
        report_progress(f"Generating output... (part {new_part_index}) evaluating {group.root_entry}")

        single_group_content = render_groups([group], new_part_index)
        single_group_bytes = get_utf8_byte_length(single_group_content)

        if single_group_bytes > max_bytes_per_part:
            raise ValueError(
                f"Cannot split output: root entry '{group.root_entry}' exceeds max size. "
                f"Part size {single_group_bytes:,} bytes > limit {max_bytes_per_part:,} bytes."
            )

        current_groups = [group]
        current_content = single_group_content
        current_bytes = single_group_bytes

    # Add final part
    if current_groups:
        final_index = len(parts) + 1
        parts.append(
            OutputSplitPart(
                index=final_index,
                file_path=build_split_output_file_path(base_config.output.file_path, final_index),
                content=current_content,
                byte_length=current_bytes,
                groups=current_groups,
            )
        )

    return parts
