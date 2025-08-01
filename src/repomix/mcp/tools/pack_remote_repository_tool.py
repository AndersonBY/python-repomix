"""Pack remote repository MCP tool - placeholder implementation."""

from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from ...shared.logger import logger
from .mcp_tool_runtime import build_mcp_tool_error_response


class PackRemoteRepositoryInput(BaseModel):
    """Input schema for pack_remote_repository tool."""

    remote: str = Field(description="GitHub repository URL or user/repo format (e.g., 'yamadashy/repomix', 'https://github.com/user/repo')")
    compress: bool = Field(
        default=False,
        description="Enable Tree-sitter compression to extract essential code signatures and structure",
    )
    include_patterns: Optional[str] = Field(default=None, description="Specify files to include using fast-glob patterns")
    ignore_patterns: Optional[str] = Field(
        default=None,
        description="Specify additional files to exclude using fast-glob patterns",
    )
    top_files_length: int = Field(
        default=10,
        description="Number of largest files by size to display in the metrics summary",
    )


def register_pack_remote_repository_tool(server: FastMCP) -> None:
    """Register the pack_remote_repository tool with the MCP server."""

    @server.tool(
        name="pack_remote_repository",
        description=(
            "Fetch, clone, and package a GitHub repository into a consolidated XML file for AI analysis. "
            "This tool clones the remote repository and processes it similarly to pack_codebase."
        ),
    )
    async def pack_remote_repository(  # pyright: ignore[reportUnusedFunction]
        input_data: PackRemoteRepositoryInput,
    ) -> Dict[str, Any]:
        """Pack a remote repository into a consolidated XML file."""

        try:
            # TODO: Implement remote repository cloning and processing
            # For now, return a placeholder error
            return build_mcp_tool_error_response(
                {"error_message": "pack_remote_repository is not yet implemented. Please use pack_codebase with a locally cloned repository."}
            )

        except Exception as error:
            logger.error(f"Error in pack_remote_repository tool: {error}")
            return build_mcp_tool_error_response({"error_message": str(error)})
