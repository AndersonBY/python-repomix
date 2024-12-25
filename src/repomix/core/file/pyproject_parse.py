"""
Version Information Parsing Module - Used for Parsing and Retrieving Project Version Information
"""

import re
from pathlib import Path
from typing import Optional

from ...shared.logger import logger


def get_version() -> str:
    """Get project version number

    Returns:
        Version number string, returns '0.0.0' if unable to retrieve
    """
    try:
        version = _read_version_from_pyproject()
        return version if version else "0.0.0"
    except Exception as error:
        logger.warn(f"Failed to read version number: {error}")
        return "0.0.0"


def _read_version_from_pyproject() -> Optional[str]:
    """Read version number from pyproject.toml file

    Returns:
        Version number string, returns None if file does not exist or reading fails
    """
    pyproject_path = Path(__file__).parent.parent.parent.parent.parent / "pyproject.toml"

    if not pyproject_path.exists():
        return None

    try:
        content = pyproject_path.read_text()
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        return match.group(1) if match else None
    except Exception as error:
        logger.warn(f"Failed to read version number: {error}")
        return None
