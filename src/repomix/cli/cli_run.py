"""
CLI Run Module - Handling Command Line Arguments and Executing Corresponding Actions
"""

import argparse
from pathlib import Path
from typing import List, Optional

from ..__init__ import __version__
from ..shared.error_handle import handle_error
from ..shared.logger import logger
from .actions.default_action import run_default_action
from .actions.init_action import run_init_action
from .actions.remote_action import run_remote_action
from .actions.version_action import run_version_action
from .types import CliOptions, CliResult


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
    parser.add_argument("--top-files-len", type=int, metavar="<number>", help="Specify maximum number of files to display")
    parser.add_argument("--output-show-line-numbers", action="store_true", help="Add line numbers to output")
    parser.add_argument(
        "--style",
        choices=["plain", "xml", "markdown"],
        metavar="<type>",
        help="Specify output style (plain, xml, markdown)",
    )
    parser.add_argument("--init", action="store_true", help="Initialize new repomix.config.json file")
    parser.add_argument("--global", dest="use_global", action="store_true", help="Use global configuration (only for --init)")
    parser.add_argument("--remote", metavar="<url>", help="Process remote Git repository")
    parser.add_argument(
        "--branch",
        metavar="<name>",
        help="Specify branch name for remote repository (can be set in config file)",
    )
    parser.add_argument("--no-security-check", action="store_true", help="Disable security check")
    parser.add_argument("--compress", action="store_true", help="Enable tree-sitter based code compression")
    parser.add_argument("--mcp", action="store_true", help="Run as MCP (Model Context Protocol) server")

    return parser


def run() -> None:
    """Run CLI command"""
    parser = create_parser()
    args = parser.parse_args()

    try:
        execute_action(args.directory, Path.cwd(), args)
    except Exception as e:
        handle_error(e)


async def run_cli(
    directories: List[str], 
    cwd: str, 
    cli_options: CliOptions
) -> Optional[CliResult]:
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
            # Use the first directory (MCP typically processes one at a time)
            directory = directories[0] if directories else "."
            
            # Run default action and get the result
            result = run_default_action(directory, cwd, options)
            
            # Return the result
            return CliResult(pack_result=result.pack_result)
            
        finally:
            # Restore original verbose setting
            logger.set_verbose(original_verbose)
            
    except Exception as e:
        logger.error(f"Error in run_cli: {e}")
        return None


def execute_action(directory: str, cwd: Path, options: argparse.Namespace) -> None:
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

    if options.mcp:
        import asyncio
        from ..mcp.mcp_server import run_mcp_server
        
        # For MCP mode, redirect logs to stderr so they don't interfere with stdio protocol
        import sys
        logger.log = lambda message="": print(str(message), file=sys.stderr)
        logger.warn = lambda message, error=None: print(f"⚠️ {message}", file=sys.stderr) 
        logger.error = lambda message: print(f"❌ {message}", file=sys.stderr)
        logger.success = lambda message: print(f"✅ {message}", file=sys.stderr)
        
        logger.log("Starting Repomix MCP Server...")
        asyncio.run(run_mcp_server())
        return

    if options.remote:
        run_remote_action(options.remote, vars(options))
        return

    run_default_action(directory, cwd, vars(options))
