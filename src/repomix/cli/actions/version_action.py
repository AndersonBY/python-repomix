"""
Version Action Module - Display Version Information
"""

from ...__init__ import __version__
from ...shared.logger import logger


def run_version_action() -> None:
    """Display version information"""
    version = __version__
    logger.log(version)
