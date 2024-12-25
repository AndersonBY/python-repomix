"""
Shared Utility Module - Provides Common Tools and Functionality
"""

from .error_handle import RepomixError, handle_error
from .logger import logger
from .process_concurrency import get_process_concurrency

__all__ = [
    "RepomixError",
    "handle_error",
    "logger",
    "get_process_concurrency",
]
