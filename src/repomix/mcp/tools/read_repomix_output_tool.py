"""Read repomix output MCP tool."""

from pathlib import Path
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from ...shared.logger import logger
from .mcp_tool_runtime import build_mcp_tool_error_response, get_output_file_path


class ReadRepomixOutputInput(BaseModel):
    """Input schema for read_repomix_output tool."""

    output_id: str = Field(description="ID of the Repomix output file to read")
    start_line: int | None = Field(
        default=None,
        description="Starting line number (1-based, inclusive). If not specified, reads from beginning.",
    )
    end_line: int | None = Field(
        default=None,
        description="Ending line number (1-based, inclusive). If not specified, reads to end.",
    )


def register_read_repomix_output_tool(server: FastMCP) -> None:
    """Register the read_repomix_output tool with the MCP server."""

    @server.tool(
        name="read_repomix_output",
        description=("Read the contents of a Repomix-generated output file. Supports partial reading with line range specification for large files."),
    )
    async def read_repomix_output(  # pyright: ignore[reportUnusedFunction]
        output_id: str, start_line: int | None = None, end_line: int | None = None
    ) -> Dict[str, Any]:
        """Read the contents of a repomix output file."""

        logger.log("📖 MCP Tool Called: read_repomix_output")
        logger.log(f"   🆔 Output ID: {output_id}")
        if start_line is not None or end_line is not None:
            logger.log(f"   📏 Line range: {start_line or 'start'}-{end_line or 'end'}")

        try:
            # Get file path from output ID
            file_path = get_output_file_path(output_id)
            if not file_path:
                error_msg = f"Output ID not found: {output_id}"
                logger.warn(f"   ⚠️ {error_msg}")
                return build_mcp_tool_error_response({"error_message": error_msg})

            logger.log(f"   📁 File path: {file_path}")

            # Check if file exists
            path = Path(file_path)
            if not path.exists():
                error_msg = f"Output file not found: {file_path}"
                logger.warn(f"   ⚠️ {error_msg}")
                return build_mcp_tool_error_response({"error_message": error_msg})

            # Read file content
            try:
                with open(file_path, encoding="utf-8") as f:
                    lines = f.readlines()

                logger.log(f"   📊 Total lines in file: {len(lines)}")

                # Apply line range if specified
                if start_line is not None or end_line is not None:
                    start_idx = (start_line - 1) if start_line else 0
                    end_idx = end_line if end_line else len(lines)

                    # Ensure valid range
                    start_idx = max(0, start_idx)
                    end_idx = min(len(lines), end_idx)

                    if start_idx >= end_idx:
                        error_msg = f"Invalid line range: start_line={start_line}, end_line={end_line}"
                        logger.warn(f"   ⚠️ {error_msg}")
                        return build_mcp_tool_error_response({"error_message": error_msg})

                    content = "".join(lines[start_idx:end_idx])
                    line_info = f" (lines {start_idx + 1}-{end_idx})"
                    logger.log(f"   📝 Returning {end_idx - start_idx} lines")
                else:
                    content = "".join(lines)
                    line_info = f" (all {len(lines)} lines)"
                    logger.log("   📝 Returning entire file")

                logger.log("   ✅ Content read successfully")

                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Content of {path.name}{line_info}:\n\n{content}",
                        }
                    ]
                }

            except UnicodeDecodeError:
                error_msg = f"Failed to decode file as UTF-8: {file_path}"
                logger.error(f"   ❌ {error_msg}")
                return build_mcp_tool_error_response({"error_message": error_msg})

        except Exception as error:
            logger.error(f"   ❌ Error in read_repomix_output tool: {error}")
            return build_mcp_tool_error_response({"error_message": str(error)})
