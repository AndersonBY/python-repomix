"""Main MCP server implementation for Repomix."""

import asyncio
import os
import signal
import sys
from mcp.server.fastmcp import FastMCP

from ..shared.logger import logger
from .silent_mode import set_mcp_silent_mode
from .tools.pack_codebase_tool import register_pack_codebase_tool
from .tools.pack_remote_repository_tool import register_pack_remote_repository_tool
from .tools.read_repomix_output_tool import register_read_repomix_output_tool
from .tools.grep_repomix_output_tool import register_grep_repomix_output_tool
from .tools.file_system_read_file_tool import register_file_system_read_file_tool
from .tools.file_system_read_directory_tool import (
    register_file_system_read_directory_tool,
)
from .tools.generate_skill_tool import register_generate_skill_tool

# MCP Server Instructions
MCP_SERVER_INSTRUCTIONS: str = (
    "Repomix MCP Server provides AI-optimized codebase analysis tools. "
    "Use pack_codebase or pack_remote_repository to consolidate code into a single XML file, "
    "then read_repomix_output and grep_repomix_output to analyze it. "
    "Perfect for code reviews, documentation generation, bug investigation, GitHub repository analysis, and understanding large codebases. "
    "Includes security scanning and supports compression for token efficiency."
)


def create_mcp_server(silent: bool = True) -> FastMCP:
    """Create and configure the Repomix MCP server.

    Args:
        silent: If True, suppress console logging output. Default is True for programmatic usage.
    """

    # Set global silent mode for MCP tools
    set_mcp_silent_mode(silent)

    if not silent:
        logger.log("🔧 Creating MCP server...")

    # Create FastMCP server instance with debug handler
    server = FastMCP(
        "repomix-mcp-server",
        instructions=MCP_SERVER_INSTRUCTIONS,
    )

    if not silent:
        logger.log("📦 Registering MCP tools...")

    # Register all tools
    register_pack_codebase_tool(server)
    if not silent:
        logger.log("  ✅ pack_codebase")

    register_pack_remote_repository_tool(server)
    if not silent:
        logger.log("  ✅ pack_remote_repository")

    register_read_repomix_output_tool(server)
    if not silent:
        logger.log("  ✅ read_repomix_output")

    register_grep_repomix_output_tool(server)
    if not silent:
        logger.log("  ✅ grep_repomix_output")

    register_file_system_read_file_tool(server)
    if not silent:
        logger.log("  ✅ file_system_read_file")

    register_file_system_read_directory_tool(server)
    if not silent:
        logger.log("  ✅ file_system_read_directory")

    register_generate_skill_tool(server)
    if not silent:
        logger.log("  ✅ generate_skill")

    if not silent:
        logger.log("🎯 Repomix MCP Server configured with 7 tools")

    logger.trace("Repomix MCP Server created and configured")
    return server


async def run_mcp_server() -> None:
    """Run the MCP server with stdio transport."""

    # Force thread-based concurrency for MCP mode
    # Process pools can cause issues with stdio-based MCP protocol
    os.environ["REPOMIX_COCURRENCY_STRATEGY"] = "thread"

    # Set up a watchdog timer to prevent zombie processes
    import threading

    def watchdog_timeout():
        """Kill the process if it runs too long without activity."""
        os._exit(1)

    # Set a 10-minute watchdog timer
    watchdog = threading.Timer(600.0, watchdog_timeout)
    watchdog.daemon = True
    watchdog.start()

    # Suppress all logging to prevent interference with MCP protocol
    import logging

    logging.getLogger().setLevel(logging.CRITICAL + 1)

    # Also suppress specific loggers that might write to stderr
    for logger_name in ["mcp", "asyncio", "concurrent.futures"]:
        logging.getLogger(logger_name).setLevel(logging.CRITICAL + 1)

    server = create_mcp_server(silent=True)

    def signal_handler() -> None:
        """Handle shutdown signals by immediately exiting."""
        # Force exit immediately using os._exit() which bypasses cleanup
        # Don't log anything as it will interfere with MCP protocol
        os._exit(0)

    # Set up signal handlers for graceful shutdown
    if sys.platform != "win32":
        # Unix-like systems
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, signal_handler)
    else:
        # Windows - use signal.signal() instead
        def win_signal_handler(signum, frame):
            # Schedule the async signal handler
            try:
                loop = asyncio.get_running_loop()
                loop.call_soon_threadsafe(signal_handler)
            except RuntimeError:
                # No event loop running, exit immediately
                logger.log("\n🛑 Received shutdown signal, exiting immediately...")
                os._exit(0)

        signal.signal(signal.SIGINT, win_signal_handler)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, win_signal_handler)

    try:
        # Add a periodic heartbeat and stdin check
        async def heartbeat():
            count = 0
            while True:
                await asyncio.sleep(30)  # Every 30 seconds
                count += 1

                # Check if stdin is closed (client disconnected)
                if sys.stdin.closed:
                    os._exit(0)

        heartbeat_task = asyncio.create_task(heartbeat())

        # Create and run server task - this will run until interrupted
        server_task = asyncio.create_task(server.run_stdio_async())

        # Run both tasks
        await asyncio.wait([server_task, heartbeat_task], return_when=asyncio.FIRST_COMPLETED)

        # Cancel the heartbeat if server completes
        heartbeat_task.cancel()

    except KeyboardInterrupt:
        # Fallback handler if signal handlers don't work
        pass

    except Exception:
        # In MCP mode, we can't log to stdout/stderr
        # Just re-raise the error
        raise

    finally:
        # Cancel the watchdog timer
        watchdog.cancel()
        # Ensure process exits
        os._exit(0)


if __name__ == "__main__":
    asyncio.run(run_mcp_server())
