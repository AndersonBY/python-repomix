"""
File Processing Module - Responsible for Processing Collected File Contents
"""

from typing import List

from ...config.config_schema import RepomixConfig
from ...shared.process_concurrency import get_process_concurrency
from .file_manipulate import get_file_manipulator
from .file_types import ProcessedFile, RawFile


def _process_single_file(args: tuple[RawFile, RepomixConfig]) -> ProcessedFile:
    """Helper function to process a single file

    Args:
        args: Tuple of (raw file object, configuration object)

    Returns:
        Processed file object
    """
    raw_file, config = args
    return ProcessedFile(path=raw_file.path, content=process_content(raw_file.content, raw_file.path, config))


def process_files(raw_files: List[RawFile], config: RepomixConfig) -> List[ProcessedFile]:
    """Process list of files

    Args:
        raw_files: List of raw files
        config: Configuration object

    Returns:
        List of processed files
    """
    # Create argument list, each element is a tuple of (raw file, configuration)
    file_args = [(raw_file, config) for raw_file in raw_files]

    with get_process_concurrency() as executor:
        processed_files = list(executor.map(_process_single_file, file_args))

    return processed_files


def process_content(content: str, file_path: str, config: RepomixConfig) -> str:
    """Process single file content

    Args:
        content: Original file content
        file_path: File path
        config: Configuration object

    Returns:
        Processed file content
    """
    processed_content = content
    manipulator = get_file_manipulator(file_path)

    # Remove comments based on configuration
    if config.output.remove_comments and manipulator:
        processed_content = manipulator.remove_comments(processed_content)

    # Remove empty lines based on configuration
    if config.output.remove_empty_lines and manipulator:
        processed_content = manipulator.remove_empty_lines(processed_content)

    # Remove leading and trailing whitespace
    processed_content = processed_content.strip()

    # Add line numbers if configured
    if config.output.show_line_numbers:
        lines = processed_content.split("\n")
        padding = len(str(len(lines)))
        numbered_lines = [f"{str(i + 1).rjust(padding)}: {line}" for i, line in enumerate(lines)]
        processed_content = "\n".join(numbered_lines)

    return processed_content
