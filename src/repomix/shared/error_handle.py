"""
Error Handling Module - Defines custom exceptions and error handling functions
"""

import sys
import traceback
from typing import Optional, Type

from .logger import logger


class RepomixError(Exception):
    """Repomix custom exception base class"""

    pass


def handle_error(error: Exception, exit_code: int = 1, error_type: Optional[Type[Exception]] = None) -> None:
    """Handle exceptions and exit the program

    Args:
        error: Exception object
        exit_code: Exit code
        error_type: Exception type (optional)
    """
    if isinstance(error, RepomixError):
        # For custom exceptions, only display the error message
        logger.error(str(error))
    elif error_type and isinstance(error, error_type):
        # For specified types of exceptions, display the error message
        logger.error(str(error))
    else:
        # For other exceptions, display the full stack trace
        if logger.is_verbose():
            traceback.print_exc()
        else:
            logger.error(f"An error occurred: {error}")
            logger.error("Use the --verbose option to see detailed error information")

    sys.exit(exit_code)
