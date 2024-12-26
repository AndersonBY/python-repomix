"""
Git Command Processing Module - Provides Git-related Functionality
"""

import subprocess
from pathlib import Path
from typing import Optional, List

from ...shared.logger import logger


def is_git_installed() -> bool:
    """Check if Git is installed

    Returns:
        True if Git is installed, False otherwise
    """
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except Exception:
        return False


def exec_git_shallow_clone(repo_url: str, target_dir: str | Path, branch: Optional[str] = None) -> None:
    """Perform Git shallow clone

    Args:
        repo_url: Repository URL
        target_dir: Target directory
        branch: Branch name (optional)

    Raises:
        subprocess.CalledProcessError: When Git command execution fails
    """
    cmd: List[str] = ["git", "clone", "--depth", "1"]

    if branch:
        cmd.extend(["-b", branch])

    cmd.extend([str(repo_url), str(target_dir)])

    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        logger.debug(f"Git clone output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Git clone failed: {e.stderr}")
        raise


def get_git_ignore_patterns(repo_dir: str | Path) -> List[str]:
    """Get ignore patterns from .gitignore

    Args:
        repo_dir: Repository directory

    Returns:
        List of ignore patterns
    """
    patterns: List[str] = []
    gitignore_path = Path(repo_dir) / ".gitignore"

    if not gitignore_path.exists():
        return patterns

    try:
        with gitignore_path.open("r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    except Exception as error:
        logger.warn(f"Failed to read .gitignore: {error}")

    return patterns
