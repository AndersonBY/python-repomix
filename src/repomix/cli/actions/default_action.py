"""
Default Action Module - Handling the Main Packaging Logic
"""

import asyncio
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

import pyperclip

from ...config.config_schema import RepomixConfig
from ...config.config_load import load_config
from ...core.repo_processor import RepoProcessor
from ...core.file.file_stdin import read_file_paths_from_stdin
from ..cli_print import (
    print_summary,
    print_security_check,
    print_top_files,
    print_completion,
)
from ..cli_spinner import Spinner
from ...shared.logger import logger
from ...shared.error_handle import RepomixError


@dataclass
class DefaultActionRunnerResult:
    """Default action runner result class

    Attributes:
        config: Merged configuration object
        pack_result: Complete repo processor result
    """

    config: RepomixConfig
    pack_result: Any  # Will be RepoProcessorResult but avoiding circular import


def run_default_action(
    directory: str | Path, cwd: str | Path, options: Dict[str, Any]
) -> DefaultActionRunnerResult:
    """Execute default action

    Args:
        directory: Target directory
        cwd: Current working directory
        options: Command line options

    Returns:
        Action execution result

    Raises:
        RepomixError: When an error occurs during execution
    """
    # Handle stdin mode
    if options.get("stdin"):
        # Validate directory arguments for stdin mode
        if directory != "." and directory != cwd:
            raise RepomixError(
                "When using --stdin, do not specify directory arguments. File paths will be read from stdin."
            )

        return _handle_stdin_processing(cwd, options)

    # Normal directory processing
    return _handle_directory_processing(directory, cwd, options)


def _handle_stdin_processing(
    cwd: str | Path, options: Dict[str, Any]
) -> DefaultActionRunnerResult:
    """Handle stdin processing workflow for file paths input.

    Args:
        cwd: Current working directory
        options: Command line options

    Returns:
        Action execution result
    """
    # Load configuration first
    cli_options_override = _build_cli_options_override(options)
    config = load_config(".", cwd, options.get("config"), cli_options_override)

    spinner = Spinner("Reading file paths from stdin...")

    try:
        # Read file paths from stdin asynchronously
        stdin_result = asyncio.run(read_file_paths_from_stdin(Path(cwd)))

        spinner.update("Packing files...")

        # Create a custom RepoProcessor that uses predefined file paths
        processor = RepoProcessor(".", config=config)
        # Set predefined file paths for stdin mode
        processor.set_predefined_file_paths(stdin_result.file_paths)
        result = processor.process()

    except Exception as error:
        spinner.fail("Error reading from stdin or during packing")
        raise error

    spinner.succeed("Packing completed successfully!")

    # Print results
    _print_results(cwd, result, config)

    return DefaultActionRunnerResult(
        config=config,
        pack_result=result,
    )


def _handle_directory_processing(
    directory: str | Path, cwd: str | Path, options: Dict[str, Any]
) -> DefaultActionRunnerResult:
    """Handle normal directory processing workflow.

    Args:
        directory: Target directory
        cwd: Current working directory
        options: Command line options

    Returns:
        Action execution result
    """
    # Load configuration
    cli_options_override = _build_cli_options_override(options)
    config = load_config(directory, cwd, options.get("config"), cli_options_override)

    # Determine if we should use remote repository from config
    if config.remote.url:
        # Use remote repository from configuration
        processor = RepoProcessor(
            repo_url=config.remote.url,
            branch=config.remote.branch if config.remote.branch else None,
            config=config,
        )
    else:
        # Use local directory
        processor = RepoProcessor(directory, config=config)
    result = processor.process()

    # Print results
    _print_results(directory, result, config)

    return DefaultActionRunnerResult(
        config=config,
        pack_result=result,
    )


def _build_cli_options_override(options: Dict[str, Any]) -> Dict[str, Any]:
    """Build CLI options override dictionary.

    Args:
        options: Raw CLI options

    Returns:
        Processed CLI options for config override
    """
    cli_options_override = {
        "output": {
            "file_path": options.get("output"),
            "style": options.get("style"),
            "show_line_numbers": options.get("output_show_line_numbers"),
            "copy_to_clipboard": options.get("copy"),
            "top_files_length": options.get("top_files_len"),
        },
        "ignore": {
            "custom_patterns": options.get("ignore", "").split(",")
            if options.get("ignore")
            else None
        },
        "include": options.get("include", "").split(",")
        if options.get("include")
        else None,
        "security": {},
        "compression": {"enabled": options.get("compress", False)},
        "remote": {
            "url": options.get("remote"),
            "branch": options.get("branch"),
        },
    }

    if "no_security_check" in options and options.get("no_security_check"):
        cli_options_override["security"]["enable_security_check"] = False
    enable_security_check_override = None
    if (
        options.get("no_security_check") is True
    ):  # Explicitly check for True set by argparse
        enable_security_check_override = False
    if enable_security_check_override is not None:
        cli_options_override["security"]["enable_security_check"] = (
            enable_security_check_override
        )

    final_cli_options = {}
    for key, value in cli_options_override.items():
        if isinstance(value, dict):
            # Filter out None values within nested dictionaries
            filtered_dict = {k: v for k, v in value.items() if v is not None}
            if filtered_dict:  # Only add non-empty dicts
                final_cli_options[key] = filtered_dict
        elif value is not None:
            final_cli_options[key] = value

    return final_cli_options


def _print_results(directory: str | Path, result: Any, config: RepomixConfig) -> None:
    """Print results of packing operation.

    Args:
        directory: Directory that was processed
        result: RepoProcessorResult
        config: Merged configuration
    """
    # Print summary information
    print_summary(
        result.total_files,
        result.total_chars,
        result.total_tokens,
        result.config.output.file_path,
        result.suspicious_files_results,
        result.config,
    )

    # Print security check results
    print_security_check(directory, result.suspicious_files_results, result.config)

    # Print list of largest files
    print_top_files(
        result.file_char_counts,
        result.file_token_counts,
        result.config.output.top_files_length,
    )

    # Copy to clipboard (if configured)
    if config.output.copy_to_clipboard:
        try:
            pyperclip.copy(result.output_content)
            logger.success("Copied to clipboard")
        except Exception as error:
            logger.warn(f"Failed to copy to clipboard: {error}")

    # Print completion message
    print_completion()
