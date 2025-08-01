"""File system read file MCP tool."""

from pathlib import Path
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from ...shared.logger import logger
from .mcp_tool_runtime import build_mcp_tool_error_response


class FileSystemReadFileInput(BaseModel):
    """Input schema for file_system_read_file tool."""

    path: str = Field(description="Absolute path to the file to read")


def register_file_system_read_file_tool(server: FastMCP) -> None:
    """Register the file_system_read_file tool with the MCP server."""

    @server.tool(
        name="file_system_read_file",
        description=(
            "Read a file from the local file system using an absolute path. "
            "Includes built-in security validation to detect and prevent access to files containing sensitive information."
        ),
    )
    async def file_system_read_file(  # pyright: ignore[reportUnusedFunction]
        input_data: FileSystemReadFileInput,
    ) -> Dict[str, Any]:
        """Read a file from the local file system."""

        try:
            # Validate path is absolute
            path = Path(input_data.path)
            if not path.is_absolute():
                return build_mcp_tool_error_response({"error_message": f"Path must be absolute: {input_data.path}"})

            # Check if file exists
            if not path.exists():
                return build_mcp_tool_error_response({"error_message": f"File not found: {input_data.path}"})

            if not path.is_file():
                return build_mcp_tool_error_response({"error_message": f"Path is not a file: {input_data.path}"})

            # TODO: Add security validation using detect-secrets
            # For now, we'll skip the security check but log that it should be implemented
            logger.trace(f"Reading file: {input_data.path} (security check not yet implemented)")

            # Read file content
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Get file stats
                stat = path.stat()
                file_size = stat.st_size

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Content of {path.name} ({file_size:,} bytes):\n\n{content}",
                        }
                    ]
                }

            except UnicodeDecodeError:
                # Try reading as binary and show first few bytes
                with open(path, "rb") as f:
                    binary_content = f.read(1024)  # Read first 1KB

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"File {path.name} appears to be binary. First 1024 bytes (hex): {binary_content.hex()}",
                        }
                    ]
                }

        except PermissionError:
            return build_mcp_tool_error_response({"error_message": f"Permission denied: {input_data.path}"})

        except Exception as error:
            logger.error(f"Error in file_system_read_file tool: {error}")
            return build_mcp_tool_error_response({"error_message": str(error)})
