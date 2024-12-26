"""
Output Generation Module - Responsible for Generating Final Output Content
"""

from typing import Dict, List

from ...shared.logger import logger
from .output_styles import get_output_style
from ...core.file.file_types import ProcessedFile
from ...config.config_schema import RepomixConfig


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
        file_tree: File tree
    Returns:
        Generated output content
    """
    # Get output style processor
    style = get_output_style(config)
    if not style:
        logger.warn(f"Unknown output style: {config.output.style}, using plain text style")
        empty_config = RepomixConfig()
        style = get_output_style(empty_config)
        assert style is not None

    # Generate output content
    output = style.generate_header()

    # Add file tree
    output += style.generate_file_tree_section(file_tree)

    # Add files section
    output += style.generate_files_section(processed_files, file_char_counts, file_token_counts)

    # Add statistics
    total_chars = sum(file_char_counts.values())
    total_tokens = sum(file_token_counts.values())

    output += style.generate_statistics(len(processed_files), total_chars, total_tokens)

    output += style.generate_footer()

    return output
