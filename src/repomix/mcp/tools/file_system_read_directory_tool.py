"""File system read directory MCP tool."""

from pathlib import Path
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from ...shared.logger import logger
from .mcp_tool_runtime import build_mcp_tool_error_response


class FileSystemReadDirectoryInput(BaseModel):
    """Input schema for file_system_read_directory tool."""

    path: str = Field(description="Absolute path to the directory to list")


def register_file_system_read_directory_tool(server: FastMCP) -> None:
    """Register the file_system_read_directory tool with the MCP server."""

    @server.tool(
        name="file_system_read_directory",
        description=(
            "List the contents of a directory using an absolute path. Returns a formatted list showing files and subdirectories with clear indicators."
        ),
    )
    async def file_system_read_directory(  # pyright: ignore[reportUnusedFunction]
        input_data: FileSystemReadDirectoryInput,
    ) -> Dict[str, Any]:
        """List the contents of a directory."""

        try:
            # Validate path is absolute
            path = Path(input_data.path)
            if not path.is_absolute():
                return build_mcp_tool_error_response({"error_message": f"Path must be absolute: {input_data.path}"})

            # Check if directory exists
            if not path.exists():
                return build_mcp_tool_error_response({"error_message": f"Directory not found: {input_data.path}"})

            if not path.is_dir():
                return build_mcp_tool_error_response({"error_message": f"Path is not a directory: {input_data.path}"})

            # List directory contents
            try:
                entries = []
                for item in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
                    if item.is_dir():
                        entries.append(f"[DIR]  {item.name}/")
                    else:
                        # Get file size
                        try:
                            size = item.stat().st_size
                            size_str = f" ({size:,} bytes)" if size < 10 * 1024 * 1024 else f" ({size / (1024 * 1024):.1f} MB)"
                        except (OSError, PermissionError):
                            size_str = " (size unknown)"

                        entries.append(f"[FILE] {item.name}{size_str}")

                if not entries:
                    content_text = f"Directory {path.name} is empty."
                else:
                    content_lines = [f"Contents of {path} ({len(entries)} items):\n"]
                    content_lines.extend(entries)
                    content_text = "\n".join(content_lines)

                return {"content": [{"type": "text", "text": content_text}]}

            except PermissionError:
                return build_mcp_tool_error_response({"error_message": f"Permission denied: {input_data.path}"})

        except Exception as error:
            logger.error(f"Error in file_system_read_directory tool: {error}")
            return build_mcp_tool_error_response({"error_message": str(error)})
