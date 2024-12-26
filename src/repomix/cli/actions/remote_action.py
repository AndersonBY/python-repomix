"""
Remote Repository Action Module - Handle remote Git repositories
"""

from pathlib import Path
from typing import Dict, Any

from ..cli_spinner import Spinner
from ...shared.logger import logger
from .default_action import run_default_action
from ...shared.error_handle import RepomixError
from ...shared.git_utils import clone_repository
from ...core.file.git_command import is_git_installed
from ...shared.fs_utils import create_temp_directory, cleanup_temp_directory, copy_output_to_current_directory


def run_remote_action(repo_url: str, options: Dict[str, Any]) -> None:
    """Handle remote repository

    Args:
        repo_url: Repository URL
        options: Command line options

    Raises:
        RepomixError: When Git is not installed or clone fails
    """
    if not is_git_installed():
        raise RepomixError("Git is not installed or not in system PATH")

    spinner = Spinner("Cloning repository...")
    temp_dir_path = create_temp_directory()

    try:
        spinner.start()

        clone_repository(repo_url, temp_dir_path, options.get("remote_branch"))

        spinner.succeed("Repository cloned successfully!")
        logger.log("")

        # Run default action on cloned repository
        result = run_default_action(temp_dir_path, Path.cwd(), options)
        filename = Path(result.config.output.file_path).name
        copy_output_to_current_directory(Path(temp_dir_path), Path.cwd(), filename)
    except Exception as error:
        spinner.fail("Error during repository cloning, cleaning up...")
        raise error
    finally:
        # Clean up temporary directory
        cleanup_temp_directory(temp_dir_path)
