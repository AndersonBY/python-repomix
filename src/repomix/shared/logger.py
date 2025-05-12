"""
Logging Module - Provides logging functionality
"""

import os
import sys
from enum import Enum
from typing import Any


class LogLevel(Enum):
    """Log level enumeration"""

    TRACE = 0
    DEBUG = 1
    INFO = 2
    SUCCESS = 3
    WARN = 4
    ERROR = 5


class Logger:
    """Logger class"""

    def __init__(self):
        """Initialize the logger"""
        self._verbose = False
        self._log_level = self._get_log_level_from_env()

    def _get_log_level_from_env(self) -> LogLevel:
        """Get log level from environment variable

        Returns:
            LogLevel: Log level, default is INFO
        """
        level_str = os.environ.get("REPOMIX_LOG_LEVEL", "INFO").upper()
        try:
            return LogLevel[level_str]
        except KeyError:
            # If the environment variable value is invalid, use INFO level by default
            print(f"⚠ Invalid log level: {level_str}, using INFO", file=sys.stderr)
            return LogLevel.INFO

    def set_verbose(self, verbose: bool) -> None:
        """Set whether to enable verbose logging

        Args:
            verbose: Whether to enable verbose logging
        """
        self._verbose = verbose
        # When setting verbose to True, if the current log level is higher than DEBUG, lower it to DEBUG
        if verbose and self._log_level.value > LogLevel.DEBUG.value:
            self._log_level = LogLevel.DEBUG

    def is_verbose(self) -> bool:
        """Get whether verbose logging is enabled

        Returns:
            Whether verbose logging is enabled
        """
        return self._verbose

    def set_log_level(self, level: LogLevel) -> None:
        """Set log level

        Args:
            level: Log level
        """
        self._log_level = level

    def get_log_level(self) -> LogLevel:
        """Get current log level

        Returns:
            Current log level
        """
        return self._log_level

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
        if self._log_level.value <= LogLevel.INFO.value:
            print(f"ℹ {message}", file=sys.stdout)

    def warn(self, message: Any, error: Any = None) -> None:
        """Log a warning message

        Args:
            message: Warning message
            error: Error object (optional)
        """
        if self._log_level.value <= LogLevel.WARN.value:
            print(f"⚠ {message}", file=sys.stderr)
            if error and self._verbose:
                print(f"  {error}", file=sys.stderr)

    def error(self, message: Any) -> None:
        """Log an error message

        Args:
            message: Error message
        """
        if self._log_level.value <= LogLevel.ERROR.value:
            print(f"✖ {message}", file=sys.stderr)

    def success(self, message: Any) -> None:
        """Log a success message

        Args:
            message: Success message
        """
        if self._log_level.value <= LogLevel.SUCCESS.value:
            print(f"✔ {message}", file=sys.stdout)

    def trace(self, message: Any) -> None:
        """Log a trace message

        Args:
            message: Trace message
        """
        if self._log_level.value <= LogLevel.TRACE.value:
            print(f"🔍 {message}", file=sys.stdout)

    def debug(self, message: Any) -> None:
        """Log a debug message

        Args:
            message: Debug message
        """
        if self._log_level.value <= LogLevel.DEBUG.value:
            print(f"🐛 {message}", file=sys.stdout)


# Create a global logger instance
logger = Logger()
