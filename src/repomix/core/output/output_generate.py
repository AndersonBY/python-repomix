"""
Output Generation Module - Responsible for Generating Final Output Content
"""

from typing import Dict, List
from pathlib import Path

from ...shared.logger import logger
from .output_styles import get_output_style
from ...core.file.file_types import ProcessedFile
from ...config.config_schema import RepomixConfig


def build_filtered_file_tree(processed_files: List[ProcessedFile]) -> Dict:
    """Build a file tree containing only the files that are actually included in the output.

    Args:
        processed_files: List of files that will be included in the output

    Returns:
        Dictionary representing the filtered file tree
    """
    tree = {}

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
) -> str:
    """Generate output content

    Args:
        processed_files: List of processed files
        config: Configuration object
        file_char_counts: File character count statistics
        file_token_counts: File token count statistics
        file_tree: Complete file tree (may contain files not in processed_files)
    Returns:
        Generated output content
    """
    # Get output style processor
    style = get_output_style(config)
    if not style:
        logger.warn(f"Unknown output style: {config.output.style_enum}, using plain text style")
        empty_config = RepomixConfig()
        style = get_output_style(empty_config)
        assert style is not None

    # Generate output content
    output = style.generate_header()

    # Add file tree if configured to do so - use filtered tree showing only included files
    if config.output.show_directory_structure:
        filtered_tree = build_filtered_file_tree(processed_files)
        output += style.generate_file_tree_section(filtered_tree)

    # Add files section
    output += style.generate_files_section(processed_files, file_char_counts, file_token_counts)

    # Add statistics
    total_chars = sum(file_char_counts.values())
    total_tokens = sum(file_token_counts.values()) if config.output.calculate_tokens else 0

    output += style.generate_statistics(len(processed_files), total_chars, total_tokens)

    output += style.generate_footer()

    return output
