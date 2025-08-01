"""
Filesystem Utilities Module - File system related helper functions
"""

import shutil
import tempfile
from pathlib import Path

from ..shared.error_handle import RepomixError
from ..shared.logger import logger


def create_temp_directory() -> Path:
    """Create temporary directory

    Returns:
        Temporary directory path
    """
    temp_dir = tempfile.mkdtemp(prefix="repomix-")
    logger.trace(f"Created temporary directory: {temp_dir}")
    return Path(temp_dir)


def cleanup_temp_directory(directory: Path) -> None:
    """Clean up temporary directory

    Args:
        directory: Temporary directory path
    """
    logger.trace(f"Cleaning up temporary directory: {directory}")
    shutil.rmtree(directory, ignore_errors=True)


def copy_output_to_current_directory(source_dir: Path, target_dir: Path, output_file_name: str) -> None:
    """Copy output file to current directory

    Args:
        source_dir: Source directory
        target_dir: Target directory
        output_file_name: Output file name

    Raises:
        RepomixError: When copy fails
    """
    source_path = source_dir / output_file_name
    target_path = target_dir / output_file_name

    try:
        logger.trace(f"Copying output file: {source_path} to {target_path}")
        target_path.write_bytes(source_path.read_bytes())
    except Exception as error:
        raise RepomixError(f"Failed to copy output file: {error}") from error
