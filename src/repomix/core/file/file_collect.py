"""
File Collection Module - Responsible for Collecting File Contents from File System
"""

from pathlib import Path
from typing import List, Optional

import chardet

from ...shared.logger import logger
from ...shared.process_concurrency import get_process_concurrency
from .file_types import RawFile


def _process_file(args: tuple[Path, str]) -> Optional[RawFile]:
    """Helper function to process a single file

    Args:
        args: Tuple of (full Path object in root_dir, relative file path)

    Returns:
        RawFile object or None
    """
    full_path, file_path = args
    return read_raw_file(full_path, file_path)


def collect_files(file_paths: List[str], root_dir: str | Path) -> List[RawFile]:
    """Collect file contents

    Args:
        file_paths: List of file paths
        root_dir: Root directory

    Returns:
        List of RawFile objects containing file contents
    """
    # Convert to Path objects
    root = Path(root_dir)
    # Create argument list, each element is a tuple of (full Path object, relative path)
    file_args = [(root / path, path) for path in file_paths]

    raw_files: List[Optional[RawFile]] = []
    with get_process_concurrency() as executor:
        raw_files = list(executor.map(_process_file, file_args))

    return [file for file in raw_files if file is not None]


def read_raw_file(full_path: Path, file_path: str) -> Optional[RawFile]:
    """Read single file content

    Args:
        full_path: Full file Path object
        file_path: Relative file path

    Returns:
        RawFile object or None (if file cannot be read)
    """
    if is_binary(full_path):
        logger.debug(f"Skipping binary file: {full_path}")
        return None

    logger.trace(f"Processing file: {full_path}")

    try:
        try:
            content = full_path.read_text(encoding="utf-8")
            return RawFile(path=file_path, content=content)
        except UnicodeDecodeError:
            content_bytes = full_path.read_bytes()
            encoding = chardet.detect(content_bytes)["encoding"] or "utf-8"
            logger.debug(f"Non-UTF8 file detected: {full_path}, using {encoding}")
            content = content_bytes.decode(encoding)
            return RawFile(path=file_path, content=content)

    except Exception as error:
        logger.warn(f"Unable to read file: {full_path}", error)
        return None


def is_binary(file_path: Path) -> bool:
    """Check if file is a binary file"""
    textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})

    def is_binary_string(bytes_data: bytes) -> bool:
        return bool(bytes_data.translate(None, textchars))

    try:
        content_bytes = file_path.read_bytes()[:1024]  # Only check first 1KB
        return is_binary_string(content_bytes)
    except Exception:
        return False
