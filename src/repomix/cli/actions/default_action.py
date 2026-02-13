"""
Default Action Module - Handling the Main Packaging Logic
"""

import asyncio
from pathlib import Path
from typing import Dict, Any, Sequence
from dataclasses import dataclass

from ...config.config_schema import RepomixConfig
from ...config.config_load import load_config
from ...core.repo_processor import RepoProcessor
from ...core.file.file_stdin import read_file_paths_from_stdin
from ...core.packager.copy_to_clipboard import copy_to_clipboard_if_enabled
from ..cli_print import (
    print_summary,
    print_security_check,
    print_top_files,
    print_completion,
)
from ..cli_spinner import Spinner
from ...shared.logger import logger
from ...shared.error_handle import RepomixError


def _parse_split_output(value: str | None) -> int | None:
    """Parse human-readable size string to bytes (e.g., '500kb', '2mb', '2.5mb').

    Args:
        value: Size string or None

    Returns:
        Size in bytes or None
    """
    if not value:
        return None
    value = value.strip().lower()
    multipliers = {"kb": 1024, "mb": 1024 * 1024, "gb": 1024 * 1024 * 1024}
    for suffix, mult in multipliers.items():
        if value.endswith(suffix):
            try:
                return int(float(value[: -len(suffix)]) * mult)
            except ValueError:
                raise RepomixError(f"Invalid size for --split-output: '{value}'") from None
    # Try plain number (bytes)
    try:
        return int(value)
    except ValueError:
        raise RepomixError(f"Invalid size for --split-output: '{value}'. Use format like 500kb, 2mb, or 2.5mb") from None


@dataclass
class DefaultActionRunnerResult:
    """Default action runner result class

    Attributes:
        config: Merged configuration object
        pack_result: Complete repo processor result
    """

    config: RepomixConfig
    pack_result: Any  # Will be RepoProcessorResult but avoiding circular import


def run_default_action(directories: Sequence[str | Path] | str | Path, cwd: str | Path, options: Dict[str, Any]) -> DefaultActionRunnerResult:
    """Execute default action

    Args:
        directories: Target directories (list or single directory for backward compatibility)
        cwd: Current working directory
        options: Command line options

    Returns:
        Action execution result

    Raises:
        RepomixError: When an error occurs during execution
    """
    # Normalize to list
    if isinstance(directories, str | Path):
        directories = [directories]

    # Validate skill-related option dependencies
    _validate_skill_options(options)

    # Validate conflicting options
    _validate_option_conflicts(options)

    # Handle stdin mode
    if options.get("stdin"):
        # Validate directory arguments for stdin mode
        first_dir = directories[0] if directories else "."
        if len(directories) > 1 or (str(first_dir) != "." and str(first_dir) != str(cwd)):
            raise RepomixError("When using --stdin, do not specify directory arguments. File paths will be read from stdin.")

        return _handle_stdin_processing(cwd, options)

    # Normal directory processing
    return _handle_directory_processing(directories, cwd, options)


def _validate_skill_options(options: Dict[str, Any]) -> None:
    """Validate skill-related option dependencies.

    Args:
        options: Command line options

    Raises:
        RepomixError: When skill options are used incorrectly
    """
    skill_generate = options.get("skill_generate")

    if options.get("skill_output") and skill_generate is None:
        raise RepomixError("--skill-output can only be used with --skill-generate")

    if options.get("force") and skill_generate is None:
        raise RepomixError("--force can only be used with --skill-generate")

    if options.get("skill_output") is not None and not str(options.get("skill_output", "")).strip():
        raise RepomixError("--skill-output path cannot be empty")


def _validate_option_conflicts(options: Dict[str, Any]) -> None:
    """Validate conflicting option combinations.

    Args:
        options: Command line options

    Raises:
        RepomixError: When conflicting options are used together
    """
    conflicts = [
        ("split_output", "stdout", "Split output requires writing to filesystem."),
        ("split_output", "skill_generate", "Skill output is a directory."),
        ("split_output", "copy", "Split output generates multiple files."),
        ("skill_generate", "stdout", "Skill output requires writing to filesystem."),
        ("skill_generate", "copy", "Skill output is a directory and cannot be copied to clipboard."),
    ]

    for opt_a, opt_b, reason in conflicts:
        if options.get(opt_a) and options.get(opt_b):
            # Convert underscores to hyphens for display
            flag_a = f"--{opt_a.replace('_', '-')}"
            flag_b = f"--{opt_b.replace('_', '-')}"
            raise RepomixError(f"{flag_a} cannot be used with {flag_b}. {reason}")


def _handle_stdin_processing(cwd: str | Path, options: Dict[str, Any]) -> DefaultActionRunnerResult:
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


def _handle_directory_processing(directories: Sequence[str | Path], cwd: str | Path, options: Dict[str, Any]) -> DefaultActionRunnerResult:
    """Handle normal directory processing workflow.

    Args:
        directories: Target directories
        cwd: Current working directory
        options: Command line options

    Returns:
        Action execution result
    """
    # Load configuration using the first directory
    first_dir = directories[0] if directories else "."
    cli_options_override = _build_cli_options_override(options)
    config = load_config(first_dir, cwd, options.get("config"), cli_options_override)

    # Determine if we should use remote repository from config
    if config.remote.url:
        # Use remote repository from configuration
        processor = RepoProcessor(
            repo_url=config.remote.url,
            branch=config.remote.branch if config.remote.branch else None,
            config=config,
        )
    else:
        # Use local directories
        processor = RepoProcessor(directories=directories, config=config)
    result = processor.process()

    # Print results
    _print_results(first_dir, result, config)

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
            "parsable_style": options.get("parsable_style"),
            "remove_comments": options.get("remove_comments"),
            "remove_empty_lines": options.get("remove_empty_lines"),
            "truncate_base64": options.get("truncate_base64"),
            "include_empty_directories": options.get("include_empty_directories"),
            "stdout": options.get("stdout"),
            "include_diffs": options.get("include_diffs"),
            "file_summary": False if options.get("no_file_summary") else None,
            "directory_structure": False if options.get("no_directory_structure") else None,
            "files": False if options.get("no_files") else None,
            "header_text": options.get("header_text"),
            "instruction_file_path": options.get("instruction_file_path"),
            "include_full_directory_structure": options.get("include_full_directory_structure") or None,
            "token_count_tree": options.get("token_count_tree"),
            "split_output": _parse_split_output(options.get("split_output")),
        },
        "ignore": {
            "custom_patterns": options.get("ignore", "").split(",") if options.get("ignore") else None,
            "use_gitignore": False if options.get("no_gitignore") else None,
            "use_dot_ignore": False if options.get("no_dot_ignore") else None,
            "use_default_ignore": False if options.get("no_default_patterns") else None,
        },
        "include": options.get("include", "").split(",") if options.get("include") else None,
        "security": {},
        "compression": {"enabled": options.get("compress", False)},
        "token_count": {"encoding": options.get("token_count_encoding")} if options.get("token_count_encoding") else {},
        "remote": {
            "url": options.get("remote"),
            "branch": options.get("remote_branch") or options.get("branch"),
        },
    }

    # Handle git-related options
    git_overrides = {}
    if options.get("no_git_sort_by_changes"):
        git_overrides["sort_by_changes"] = False
    if options.get("include_diffs"):
        git_overrides["include_diffs"] = True
    if options.get("include_logs"):
        git_overrides["include_logs"] = True
    if options.get("include_logs_count") is not None:
        git_overrides["include_logs_count"] = options["include_logs_count"]
    if git_overrides:
        cli_options_override["output"]["git"] = git_overrides

    # Handle skill generation
    skill_generate = options.get("skill_generate")
    if skill_generate is not None:
        cli_options_override["skill_generate"] = skill_generate

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
            copy_to_clipboard_if_enabled(result.output_content, config)
        except Exception as error:
            logger.warn(f"Failed to copy to clipboard: {error}")

    # Print completion message
    print_completion()
