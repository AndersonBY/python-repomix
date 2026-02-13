"""
CLI Run Module - Handling Command Line Arguments and Executing Corresponding Actions
"""

import re
import sys
import asyncio
import argparse
from pathlib import Path
from typing import Dict, List, NoReturn

from ..__init__ import __version__
from ..shared.error_handle import handle_error, RepomixError
from ..shared.logger import logger, LogLevel
from .actions.default_action import run_default_action
from .actions.init_action import run_init_action
from .actions.remote_action import run_remote_action
from .actions.version_action import run_version_action
from .types import CliOptions, CliResult

# Semantic suggestion map: maps conceptually related terms to valid options
SEMANTIC_SUGGESTION_MAP: Dict[str, List[str]] = {
    "exclude": ["--ignore"],
    "reject": ["--ignore"],
    "omit": ["--ignore"],
    "skip": ["--ignore"],
    "blacklist": ["--ignore"],
    "save": ["--output"],
    "export": ["--output"],
    "out": ["--output"],
    "file": ["--output"],
    "format": ["--style"],
    "type": ["--style"],
    "syntax": ["--style"],
    "debug": ["--verbose"],
    "detailed": ["--verbose"],
    "silent": ["--quiet"],
    "mute": ["--quiet"],
    "add": ["--include"],
    "with": ["--include"],
    "whitelist": ["--include"],
    "clone": ["--remote"],
    "git": ["--remote"],
    "minimize": ["--compress"],
    "reduce": ["--compress"],
    "strip-comments": ["--remove-comments"],
    "no-comments": ["--remove-comments"],
    "print": ["--stdout"],
    "console": ["--stdout"],
    "terminal": ["--stdout"],
    "pipe": ["--stdin"],
}


class RepomixArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser with semantic suggestions for unknown options."""

    def error(self, message: str) -> NoReturn:
        """Override error to provide semantic suggestions for unknown options."""
        # Check if this is an "unrecognized arguments" error
        match = re.search(r"unrecognized arguments: (-{1,2}\S+)", message)
        if match:
            unknown_option = match.group(1)
            clean_option = unknown_option.lstrip("-")

            semantic_matches = SEMANTIC_SUGGESTION_MAP.get(clean_option)
            if semantic_matches:
                self.print_usage(sys.stderr)
                suggestion = " or ".join(semantic_matches)
                self.exit(2, f"error: Unknown option: {unknown_option}\nDid you mean: {suggestion}?\n")

        # Fall back to default argparse error handling
        super().error(message)


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = RepomixArgumentParser(description="Repomix - Code Repository Packaging Tool")

    # Positional arguments
    parser.add_argument(
        "directories",
        nargs="*",
        default=["."],
        help="Target directories to process (defaults to current directory)",
    )

    # Optional arguments
    parser.add_argument("-v", "--version", action="store_true", help="Display version information")
    parser.add_argument("-o", "--output", metavar="<file>", help="Specify output file name")
    parser.add_argument(
        "--include",
        metavar="<patterns>",
        help="List of include patterns (comma-separated)",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        metavar="<patterns>",
        help="Additional ignore patterns (comma-separated)",
    )
    parser.add_argument("-c", "--config", metavar="<path>", help="Custom configuration file path")
    parser.add_argument("--copy", action="store_true", help="Copy generated output to system clipboard")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--quiet", action="store_true", help="Suppress all console output except errors")
    parser.add_argument(
        "--top-files-len",
        type=int,
        metavar="<number>",
        help="Specify maximum number of files to display",
    )
    parser.add_argument(
        "--output-show-line-numbers",
        action="store_true",
        help="Add line numbers to output",
    )
    parser.add_argument(
        "--style",
        choices=["plain", "xml", "markdown", "json"],
        metavar="<type>",
        help="Specify output style (plain, xml, markdown, json)",
    )
    parser.add_argument("--init", action="store_true", help="Initialize new repomix.config.json file")
    parser.add_argument(
        "--global",
        dest="use_global",
        action="store_true",
        help="Use global configuration (only for --init)",
    )
    parser.add_argument("--remote", metavar="<url>", help="Process remote Git repository")
    parser.add_argument(
        "--remote-branch",
        metavar="<name>",
        help="Specify branch, tag, or commit for remote repository",
    )
    # Keep --branch as deprecated alias for backward compatibility
    parser.add_argument(
        "--branch",
        metavar="<name>",
        help=argparse.SUPPRESS,  # Hidden, deprecated in favor of --remote-branch
    )
    parser.add_argument("--no-security-check", action="store_true", help="Disable security check")
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Enable tree-sitter based code compression",
    )
    parser.add_argument("--mcp", action="store_true", help="Run as MCP (Model Context Protocol) server")
    parser.add_argument("--stdin", action="store_true", help="Read file paths from standard input")
    parser.add_argument(
        "--parsable-style",
        action="store_true",
        help="By escaping and formatting, ensure the output is parsable as a document of its type",
    )
    parser.add_argument("--stdout", action="store_true", help="Output to stdout instead of writing to a file")
    parser.add_argument("--remove-comments", action="store_true", help="Remove comments from source code")
    parser.add_argument("--remove-empty-lines", action="store_true", help="Remove empty lines from source code")
    parser.add_argument("--truncate-base64", action="store_true", help="Enable truncation of base64 data strings")
    parser.add_argument("--include-empty-directories", action="store_true", help="Include empty directories in the output")
    parser.add_argument("--include-diffs", action="store_true", help="Include git diffs in the output")
    parser.add_argument("--no-file-summary", action="store_true", help="Omit the file summary section from output")
    parser.add_argument("--no-directory-structure", action="store_true", help="Omit the directory tree visualization from output")
    parser.add_argument("--no-files", action="store_true", help="Generate metadata only without file contents")
    parser.add_argument(
        "--token-count-encoding",
        metavar="<encoding>",
        help="Tokenizer model for counting: o200k_base (GPT-4o), cl100k_base (GPT-3.5/4), etc.",
    )
    parser.add_argument(
        "--token-count-tree",
        nargs="?",
        const=True,
        default=None,
        metavar="<threshold>",
        help="Show file tree with token counts; optional threshold to show only files with ≥N tokens",
    )
    parser.add_argument("--header-text", metavar="<text>", help="Custom text to include at the beginning of the output")
    parser.add_argument("--instruction-file-path", metavar="<path>", help="Path to file containing custom instructions to include in output")
    parser.add_argument("--split-output", metavar="<size>", help="Split output into multiple numbered files (e.g., 500kb, 2mb)")
    parser.add_argument("--include-full-directory-structure", action="store_true", help="Show entire repository tree even when using --include patterns")
    parser.add_argument("--no-git-sort-by-changes", action="store_true", help="Don't sort files by git change frequency")
    parser.add_argument("--include-logs", action="store_true", help="Add git commit history with messages and changed files")
    parser.add_argument("--include-logs-count", type=int, metavar="<count>", help="Number of recent commits to include with --include-logs (default: 50)")
    parser.add_argument("--no-gitignore", action="store_true", help="Don't use .gitignore rules for filtering files")
    parser.add_argument("--no-dot-ignore", action="store_true", help="Don't use .ignore rules for filtering files")
    parser.add_argument("--no-default-patterns", action="store_true", help="Don't apply built-in ignore patterns")

    # Skill Generation
    parser.add_argument(
        "--skill-generate",
        nargs="?",
        const=True,
        default=None,
        metavar="<name>",
        help="Generate Claude Agent Skills format output to .claude/skills/<name>/ directory",
    )
    parser.add_argument("--skill-output", metavar="<path>", help="Specify skill output directory path directly")
    parser.add_argument("-f", "--force", action="store_true", help="Skip all confirmation prompts (currently: skill directory overwrite)")

    return parser


def run() -> None:
    """Run CLI command"""
    parser = create_parser()
    args = parser.parse_args()

    try:
        execute_action(args.directories, Path.cwd(), args)
    except Exception as e:
        handle_error(e)


async def run_cli(directories: List[str], cwd: str, cli_options: CliOptions) -> CliResult | None:
    """Run CLI programmatically for MCP tools.

    Args:
        directories: List of directories to process (usually just one)
        cwd: Current working directory
        cli_options: CLI options object

    Returns:
        CliResult with pack_result
    """

    try:
        # Convert CliOptions to dict format expected by default_action
        options = {
            "output": cli_options.output,
            "style": cli_options.style,
            "output_show_line_numbers": False,
            "copy": False,
            "top_files_len": cli_options.top_files_len,
            "ignore": cli_options.ignore,
            "include": cli_options.include,
            "no_security_check": not cli_options.security_check,
            "remote": None,
            "branch": None,
            "compress": cli_options.compress,
        }

        # Set quiet mode if requested
        original_verbose = logger.is_verbose()
        logger.set_verbose(not cli_options.quiet)

        try:
            # Normalize empty directories to default
            dirs = directories if directories else ["."]

            # Run default action in a separate thread to avoid blocking the event loop
            result = await asyncio.to_thread(run_default_action, dirs, cwd, options)

            # Return the result
            return CliResult(pack_result=result.pack_result)

        finally:
            # Restore original verbose setting
            logger.set_verbose(original_verbose)

    except Exception as e:
        logger.error(f"Error in run_cli: {e}")
        return None


def execute_action(directories: List[str], cwd: Path, options: argparse.Namespace) -> None:
    """Execute corresponding action

    Args:
        directories: Target directories
        cwd: Current working directory
        options: Command line options
    """
    logger.set_verbose(options.verbose)

    # Handle quiet and verbose conflict
    if getattr(options, 'quiet', False) and getattr(options, 'verbose', False):
        raise RepomixError("--quiet and --verbose cannot be used together")

    # Set log level based on verbose and quiet flags
    if getattr(options, 'quiet', False):
        logger.set_log_level(LogLevel.SILENT)
    elif options.verbose:
        logger.set_log_level(LogLevel.DEBUG)

    if options.version:
        run_version_action()
        return

    logger.log(f"\n📦 Repomix v{__version__}\n")

    if options.init:
        run_init_action(cwd, options.use_global)
        return

    if options.mcp:
        from ..mcp.mcp_server import run_mcp_server

        # MCP mode runs in complete silence to avoid interfering with stdio protocol
        asyncio.run(run_mcp_server())
        return

    if options.remote:
        run_remote_action(options.remote, vars(options))
        return

    run_default_action(directories, cwd, vars(options))
