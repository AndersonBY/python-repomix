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
from .tools.file_system_read_directory_tool import register_file_system_read_directory_tool

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
    
    # Create FastMCP server instance
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
    
    if not silent:
        logger.log("🎯 Repomix MCP Server configured with 6 tools")
    logger.trace("Repomix MCP Server created and configured")
    return server


async def run_mcp_server() -> None:
    """Run the MCP server with stdio transport."""
    server = create_mcp_server(silent=False)
    
    def signal_handler() -> None:
        """Handle shutdown signals by immediately exiting."""
        logger.log("\n🛑 Received shutdown signal, exiting immediately...")
        # Force exit immediately using os._exit() which bypasses cleanup
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
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, win_signal_handler)
    
    try:
        logger.log("🚀 Starting Repomix MCP Server on stdio transport...")
        logger.log("📡 Waiting for MCP client connections...")
        logger.log("💡 Use Ctrl+C to stop the server")
        logger.log("─" * 50)
        
        # Create and run server task - this will run until interrupted
        server_task = asyncio.create_task(server.run_stdio_async())
        await server_task
        
    except KeyboardInterrupt:
        # Fallback handler if signal handlers don't work
        logger.log("\n🛑 Received keyboard interrupt, shutting down...")
        
    except Exception as error:
        logger.error(f"❌ MCP server error: {error}")
        raise
        
    finally:
        logger.log("✅ Repomix MCP Server shutdown complete")


if __name__ == "__main__":
    asyncio.run(run_mcp_server())