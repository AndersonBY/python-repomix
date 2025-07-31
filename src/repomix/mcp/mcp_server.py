"""Main MCP server implementation for Repomix."""

import asyncio
from typing import Callable, Awaitable
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
    
    try:
        logger.log("🚀 Starting Repomix MCP Server on stdio transport...")
        logger.log("📡 Waiting for MCP client connections...")
        logger.log("💡 Use Ctrl+C to stop the server")
        logger.log("─" * 50)
        
        # Add a hook to log when we receive requests
        original_run_stdio: Callable[[], Awaitable[None]] = server.run_stdio_async
        
        async def logged_run_stdio() -> None:
            logger.trace("MCP server stdio transport started")
            await original_run_stdio()
            
        await logged_run_stdio()
        
    except KeyboardInterrupt:
        logger.log("\n🛑 Received keyboard interrupt, shutting down...")
        
    except Exception as error:
        logger.error(f"❌ MCP server error: {error}")
        raise
        
    finally:
        logger.log("✅ Repomix MCP Server shutdown complete")


if __name__ == "__main__":
    asyncio.run(run_mcp_server())