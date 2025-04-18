"""
Default Action Module - Handling the Main Packaging Logic
"""

from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

import pyperclip

from ...config.config_schema import RepomixConfig
from ...config.config_load import load_config
from ...core.repo_processor import RepoProcessor
from ..cli_print import (
    print_summary,
    print_security_check,
    print_top_files,
    print_completion,
)
from ...shared.logger import logger


@dataclass
class DefaultActionRunnerResult:
    """Default action runner result class

    Attributes:
        config: Merged configuration object
        total_files: Total number of files
        total_chars: Total character count
        total_tokens: Total token count
    """

    config: RepomixConfig
    total_files: int
    total_chars: int
    total_tokens: int


def run_default_action(directory: str | Path, cwd: str | Path, options: Dict[str, Any]) -> DefaultActionRunnerResult:
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
    # Prepare CLI overrides, only including options explicitly set or implied by flags
    cli_options_override = {
        "output": {
            "file_path": options.get("output"),
            "style": options.get("style"),
            "show_line_numbers": options.get("output_show_line_numbers"),
            "copy_to_clipboard": options.get("copy"),
            "top_files_length": options.get("top_files_len"),
        },
        "ignore": {"custom_patterns": options.get("ignore", "").split(",") if options.get("ignore") else None},
        "include": options.get("include", "").split(",") if options.get("include") else None,
        "security": {},
    }

    if "no_security_check" in options and options.get("no_security_check"):
        cli_options_override["security"]["enable_security_check"] = False
    enable_security_check_override = None
    if options.get("no_security_check") is True:  # Explicitly check for True set by argparse
        enable_security_check_override = False
    if enable_security_check_override is not None:
        cli_options_override["security"]["enable_security_check"] = enable_security_check_override

    final_cli_options = {}
    for key, value in cli_options_override.items():
        if isinstance(value, dict):
            # Filter out None values within nested dictionaries
            filtered_dict = {k: v for k, v in value.items() if v is not None}
            if filtered_dict:  # Only add non-empty dicts
                final_cli_options[key] = filtered_dict
        elif value is not None:
            final_cli_options[key] = value

    # Load configuration using the refined overrides
    config = load_config(
        directory,
        cwd,
        options.get("config"),
        final_cli_options,
    )

    processor = RepoProcessor(directory, config=config)
    result = processor.process()

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

    return DefaultActionRunnerResult(
        config=config,
        total_files=result.total_files,
        total_chars=result.total_chars,
        total_tokens=result.total_tokens,
    )
