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
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            check=True,
        )
        return True
    except Exception:
        return False


def is_git_repository(directory: str | Path) -> bool:
    """Check if the directory is a Git repository

    Args:
        directory: Directory to check

    Returns:
        True if the directory is a Git repository, False otherwise
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except Exception:
        return False


def exec_git_diff(directory: str | Path, options: Optional[List[str]] = None) -> str:
    """Execute git diff command

    Args:
        directory: Repository directory
        options: Additional git diff options (e.g., ['--cached'] for staged changes)

    Returns:
        Git diff output string

    Raises:
        subprocess.CalledProcessError: When Git command execution fails
    """
    cmd = ["git", "-C", str(directory), "diff", "--no-color"]
    if options:
        cmd.extend(options)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout or ""
    except subprocess.CalledProcessError as e:
        logger.trace(f"Failed to execute git diff: {e.stderr}")
        raise


def exec_git_log(
    directory: str | Path,
    max_commits: int = 50,
    separator: str = "---COMMIT---",
) -> str:
    """Execute git log command

    Args:
        directory: Repository directory
        max_commits: Maximum number of commits to retrieve
        separator: Separator string between commits

    Returns:
        Git log output string

    Raises:
        subprocess.CalledProcessError: When Git command execution fails
    """
    cmd = [
        "git",
        "-C",
        str(directory),
        "log",
        f"--pretty=format:{separator}%ad|%s",
        "--date=iso",
        "--name-only",
        "-n",
        str(max_commits),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout or ""
    except subprocess.CalledProcessError as e:
        logger.trace(f"Failed to execute git log: {e.stderr}")
        raise


def exec_git_log_filenames(directory: str | Path, max_commits: int = 100) -> List[str]:
    """Get list of filenames from git log

    Args:
        directory: Repository directory
        max_commits: Maximum number of commits to check

    Returns:
        List of filenames that have been changed
    """
    cmd = [
        "git",
        "-C",
        str(directory),
        "log",
        "--pretty=format:",
        "--name-only",
        "-n",
        str(max_commits),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Filter out empty lines and return unique filenames
        filenames = [line.strip() for line in result.stdout.split("\n") if line.strip()]
        return filenames
    except subprocess.CalledProcessError as e:
        logger.trace(f"Failed to get git log filenames: {e.stderr}")
        return []


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
        result = subprocess.run(cmd, capture_output=True, check=True, text=True)
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
