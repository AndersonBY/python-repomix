"""
CLI Run Module - Handling Command Line Arguments and Executing Corresponding Actions
"""

import argparse
from pathlib import Path

from ..__init__ import __version__
from ..shared.error_handle import handle_error
from ..shared.logger import logger
from .actions.default_action import run_default_action
from .actions.init_action import run_init_action
from .actions.remote_action import run_remote_action
from .actions.version_action import run_version_action


def create_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(description="Repomix - Code Repository Packaging Tool")

    # Positional arguments
    parser.add_argument("directory", nargs="?", default=".", help="Target directory, defaults to current directory")

    # Optional arguments
    parser.add_argument("-v", "--version", action="store_true", help="Display version information")
    parser.add_argument("-o", "--output", metavar="<file>", help="Specify output file name")
    parser.add_argument("--include", metavar="<patterns>", help="List of include patterns (comma-separated)")
    parser.add_argument("-i", "--ignore", metavar="<patterns>", help="Additional ignore patterns (comma-separated)")
    parser.add_argument("-c", "--config", metavar="<path>", help="Custom configuration file path")
    parser.add_argument("--copy", action="store_true", help="Copy generated output to system clipboard")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--top-files-len", type=int, metavar="<number>", help="Specify maximum number of files to display"
    )
    parser.add_argument("--output-show-line-numbers", action="store_true", help="Add line numbers to output")
    parser.add_argument(
        "--style",
        choices=["plain", "xml", "markdown"],
        metavar="<type>",
        help="Specify output style (plain, xml, markdown)",
    )
    parser.add_argument("--init", action="store_true", help="Initialize new repomix.config.json file")
    parser.add_argument(
        "--global", dest="use_global", action="store_true", help="Use global configuration (only for --init)"
    )
    parser.add_argument("--remote", metavar="<url>", help="Process remote Git repository")
    parser.add_argument(
        "--remote-branch",
        metavar="<name>",
        help="Specify remote branch name, tag, or commit hash (defaults to repository default branch)",
    )
    parser.add_argument("--no-security-check", action="store_true", help="Disable security check")

    return parser


def run() -> None:
    """Run CLI command"""
    parser = create_parser()
    args = parser.parse_args()

    try:
        execute_action(args.directory, Path.cwd(), args)
    except Exception as e:
        handle_error(e)


def execute_action(directory: str, cwd: str | Path, options: argparse.Namespace) -> None:
    """Execute corresponding action

    Args:
        directory: Target directory
        cwd: Current working directory
        options: Command line options
    """
    logger.set_verbose(options.verbose)

    if options.version:
        run_version_action()
        return

    logger.log(f"\n📦 Repomix v{__version__}\n")

    if options.init:
        run_init_action(cwd, options.use_global)
        return

    if options.remote:
        run_remote_action(options.remote, vars(options))
        return

    run_default_action(directory, cwd, vars(options))
