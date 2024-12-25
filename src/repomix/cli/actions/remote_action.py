"""
Remote Repository Action Module - Handle remote Git repositories
"""

import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional

from ...core.file.git_command import exec_git_shallow_clone, is_git_installed
from ...shared.error_handle import RepomixError
from ...shared.logger import logger
from .default_action import run_default_action
from ..cli_spinner import Spinner


def run_remote_action(repo_url: str, options: Dict[str, Any], deps: Optional[Dict[str, Any]] = None) -> None:
    """Handle remote repository

    Args:
        repo_url: Repository URL
        options: Command line options
        deps: Dependency injection (for testing)

    Raises:
        RepomixError: When Git is not installed or clone fails
    """
    if deps is None:
        deps = {"is_git_installed": is_git_installed, "exec_git_shallow_clone": exec_git_shallow_clone}

    if not deps["is_git_installed"]():
        raise RepomixError("Git is not installed or not in system PATH")

    spinner = Spinner("Cloning repository...")
    temp_dir_path = create_temp_directory()

    try:
        spinner.start()

        # Clone repository
        clone_repository(
            format_git_url(repo_url),
            temp_dir_path,
            options.get("remote_branch"),
            {"exec_git_shallow_clone": deps["exec_git_shallow_clone"]},
        )

        spinner.succeed("Repository cloned successfully!")
        logger.log("")

        # Run default action on cloned repository
        result = run_default_action(temp_dir_path, temp_dir_path, options)
        filename = Path(result.config.output.file_path).name
        copy_output_to_current_directory(Path(temp_dir_path), Path.cwd(), filename)
    except Exception as error:
        spinner.fail("Error during repository cloning, cleaning up...")
        raise error
    finally:
        # Clean up temporary directory
        cleanup_temp_directory(temp_dir_path)


def format_git_url(url: str) -> str:
    """Format Git URL

    Args:
        url: Original URL

    Returns:
        Formatted URL
    """
    # If URL format is owner/repo, convert to GitHub URL
    if re.match(r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$", url):
        logger.trace(f"Formatting GitHub shorthand: {url}")
        return f"https://github.com/{url}.git"

    # If HTTPS URL without .git suffix, add .git
    if url.startswith("https://") and not url.endswith(".git"):
        logger.trace(f"Adding .git suffix to HTTPS URL: {url}")
        return f"{url}.git"

    return url


def create_temp_directory() -> str:
    """Create temporary directory

    Returns:
        Temporary directory path
    """
    temp_dir = tempfile.mkdtemp(prefix="repomix-")
    logger.trace(f"Created temporary directory: {temp_dir}")
    return temp_dir


def clone_repository(
    url: str, directory: str, branch: Optional[str] = None, deps: Optional[Dict[str, Any]] = None
) -> None:
    """Clone repository

    Args:
        url: Repository URL
        directory: Target directory
        branch: Branch name (optional)
        deps: Dependency injection (for testing)

    Raises:
        RepomixError: When clone fails
    """
    if deps is None:
        deps = {"exec_git_shallow_clone": exec_git_shallow_clone}

    logger.log(f"Cloning repository: {url} to temporary directory: {directory}")
    logger.log("")

    try:
        deps["exec_git_shallow_clone"](url, directory, branch)
    except Exception as error:
        raise RepomixError(f"Repository clone failed: {error}")


def cleanup_temp_directory(directory: str) -> None:
    """Clean up temporary directory

    Args:
        directory: Temporary directory path
    """
    logger.trace(f"Cleaning up temporary directory: {directory}")
    shutil.rmtree(directory, ignore_errors=True)


def copy_output_to_current_directory(source_dir: Path, target_dir: Path, output_file_name: str) -> None:
    """Copy output file to current directory

    Args:
        source_dir: Source directory
        target_dir: Target directory
        output_file_name: Output file name

    Raises:
        RepomixError: When copy fails
    """
    source_path = source_dir / output_file_name
    target_path = target_dir / output_file_name

    try:
        logger.trace(f"Copying output file: {source_path} to {target_path}")
        target_path.write_bytes(source_path.read_bytes())
    except Exception as error:
        raise RepomixError(f"Failed to copy output file: {error}")
