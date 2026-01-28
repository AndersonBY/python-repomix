"""
Output Generation Module - Responsible for Generating Final Output Content
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from ...shared.logger import logger
from .output_styles import get_output_style
from .output_styles.json_style import JsonStyle
from ...core.file.file_types import ProcessedFile
from ...config.config_schema import RepomixConfig, RepomixOutputStyle


def build_filtered_file_tree(processed_files: List[ProcessedFile]) -> Dict:
    """Build a file tree containing only the files that are actually included in the output.

    Args:
        processed_files: List of files that will be included in the output

    Returns:
        Dictionary representing the filtered file tree
    """
    tree: Dict[str, Any] = {}

    for processed_file in processed_files:
        # Split the path into parts
        path_parts = Path(processed_file.path).parts
        current_level = tree

        # Navigate/create the directory structure
        for i, part in enumerate(path_parts):
            if i == len(path_parts) - 1:
                # This is the file (leaf node)
                current_level[part] = ""
            else:
                # This is a directory
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

    return tree


def generate_output(
    processed_files: List[ProcessedFile],
    config: RepomixConfig,
    file_char_counts: Dict[str, int],
    file_token_counts: Dict[str, int],
    file_tree: Dict,
    git_diff_result: Optional[Any] = None,
    git_log_result: Optional[Any] = None,
) -> str:
    """Generate output content

    Args:
        processed_files: List of processed files
        config: Configuration object
        file_char_counts: File character count statistics
        file_token_counts: File token count statistics
        file_tree: File tree (full or filtered based on config)
        git_diff_result: Git diff result (optional)
        git_log_result: Git log result (optional)
    Returns:
        Generated output content
    """
    # Calculate statistics
    total_chars = sum(file_char_counts.values())
    total_tokens = sum(file_token_counts.values()) if config.output.calculate_tokens else 0

    # Determine which file tree to use for display
    if config.output.include_full_directory_structure:
        # Use the full file tree passed in (already built without filtering)
        display_tree = file_tree
    else:
        # Build filtered tree showing only included files
        display_tree = build_filtered_file_tree(processed_files)

    # Handle JSON output style specially
    if config.output.style_enum == RepomixOutputStyle.JSON:
        json_style = JsonStyle(config)
        return json_style.generate_json_output(
            files=processed_files,
            file_char_counts=file_char_counts,
            file_token_counts=file_token_counts,
            file_tree=display_tree,
            total_files=len(processed_files),
            total_chars=total_chars,
            total_tokens=total_tokens,
            git_diff_result=git_diff_result,
            git_log_result=git_log_result,
        )

    # Get output style processor for other styles
    style = get_output_style(config)
    if not style:
        logger.warn(f"Unknown output style: {config.output.style_enum}, using plain text style")
        empty_config = RepomixConfig()
        style = get_output_style(empty_config)
        assert style is not None

    # Generate output content
    output = style.generate_header()

    # Add file tree if configured to do so
    if config.output.show_directory_structure:
        output += style.generate_file_tree_section(display_tree)

    # Add files section
    output += style.generate_files_section(processed_files, file_char_counts, file_token_counts)

    # Add git diff section if enabled
    if config.output.git.include_diffs and git_diff_result:
        output += style.generate_git_diff_section(
            work_tree_diff=git_diff_result.work_tree_diff_content,
            staged_diff=git_diff_result.staged_diff_content,
        )

    # Add git log section if enabled
    if config.output.git.include_logs and git_log_result:
        output += style.generate_git_log_section(commits=git_log_result.commits)

    # Add statistics
    output += style.generate_statistics(len(processed_files), total_chars, total_tokens)

    output += style.generate_footer()

    return output
