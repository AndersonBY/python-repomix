"""
Permission Check Module - Used for Checking File and Directory Access Permissions
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class PermissionError(Exception):
    """Permission Error Exception Class

    Attributes:
        path: Path where permission error occurred
        message: Error message
    """

    path: str
    message: str


@dataclass
class PermissionCheckResult:
    """Permission Check Result Class

    Attributes:
        has_permission: Whether permission is granted
        error: Stores error information if no permission
    """

    has_permission: bool
    error: Optional[Exception] = None


def check_file_permission(file_path: str | Path) -> PermissionCheckResult:
    """Check file access permissions

    Args:
        file_path: File path

    Returns:
        Permission check result
    """
    try:
        # Check if file is readable
        Path(file_path).read_text()
        return PermissionCheckResult(has_permission=True)
    except PermissionError as e:
        return PermissionCheckResult(
            has_permission=False,
            error=PermissionError(path=str(file_path), message=f"No permission to access file: {e}"),
        )
    except Exception as e:
        return PermissionCheckResult(has_permission=False, error=e)


def check_directory_permission(directory: str | Path) -> PermissionCheckResult:
    """Check directory access permissions

    Args:
        directory: Directory path

    Returns:
        Permission check result
    """
    try:
        # Check if directory contents can be listed
        list(Path(directory).iterdir())
        return PermissionCheckResult(has_permission=True)
    except PermissionError as e:
        return PermissionCheckResult(
            has_permission=False,
            error=PermissionError(path=str(directory), message=f"No permission to access directory: {e}"),
        )
    except Exception as e:
        return PermissionCheckResult(has_permission=False, error=e)
