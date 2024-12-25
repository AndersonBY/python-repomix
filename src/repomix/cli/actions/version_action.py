"""
Version Action Module - Display Version Information
"""

from ...core.file.pyproject_parse import get_version
from ...shared.logger import logger


def run_version_action() -> None:
    """Display version information"""
    version = get_version()
    logger.log(version)
