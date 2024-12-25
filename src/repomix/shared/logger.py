"""
Logging Module - Provides logging functionality
"""

import sys
from typing import Any


class Logger:
    """Logger class"""

    def __init__(self):
        """Initialize the logger"""
        self._verbose = False

    def set_verbose(self, verbose: bool) -> None:
        """Set whether to enable verbose logging

        Args:
            verbose: Whether to enable verbose logging
        """
        self._verbose = verbose

    def is_verbose(self) -> bool:
        """Get whether verbose logging is enabled

        Returns:
            Whether verbose logging is enabled
        """
        return self._verbose

    def log(self, message: Any = "") -> None:
        """Log a normal message

        Args:
            message: Log message
        """
        print(str(message), file=sys.stdout)

    def info(self, message: Any) -> None:
        """Log an informational message

        Args:
            message: Log message
        """
        print(f"ℹ {message}", file=sys.stdout)

    def warn(self, message: Any, error: Any = None) -> None:
        """Log a warning message

        Args:
            message: Warning message
            error: Error object (optional)
        """
        print(f"⚠ {message}", file=sys.stderr)
        if error and self._verbose:
            print(f"  {error}", file=sys.stderr)

    def error(self, message: Any) -> None:
        """Log an error message

        Args:
            message: Error message
        """
        print(f"✖ {message}", file=sys.stderr)

    def success(self, message: Any) -> None:
        """Log a success message

        Args:
            message: Success message
        """
        print(f"✔ {message}", file=sys.stdout)

    def trace(self, message: Any) -> None:
        """Log a trace message

        Args:
            message: Trace message
        """
        if self._verbose:
            print(f"🔍 {message}", file=sys.stdout)

    def debug(self, message: Any) -> None:
        """Log a debug message

        Args:
            message: Debug message
        """
        if self._verbose:
            print(f"🐛 {message}", file=sys.stdout)


# Create a global logger instance
logger = Logger()
