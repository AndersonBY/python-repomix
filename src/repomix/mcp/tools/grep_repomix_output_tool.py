"""Grep repomix output MCP tool."""

import re
from pathlib import Path
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from ...shared.logger import logger
from .mcp_tool_runtime import build_mcp_tool_error_response, get_output_file_path


class GrepRepomixOutputInput(BaseModel):
    """Input schema for grep_repomix_output tool."""

    output_id: str = Field(description="ID of the Repomix output file to search")
    pattern: str = Field(description="Search pattern (JavaScript RegExp regular expression syntax)")
    context_lines: Optional[int] = Field(
        default=0,
        description="Number of context lines to show before and after each match (like grep -C). Overridden by before_lines/after_lines if specified.",
    )
    before_lines: Optional[int] = Field(
        default=None,
        description="Number of context lines to show before each match (like grep -B). Takes precedence over context_lines.",
    )
    after_lines: Optional[int] = Field(
        default=None,
        description="Number of context lines to show after each match (like grep -A). Takes precedence over context_lines.",
    )
    ignore_case: bool = Field(default=False, description="Perform case-insensitive matching")


def register_grep_repomix_output_tool(server: FastMCP) -> None:
    """Register the grep_repomix_output tool with the MCP server."""

    @server.tool(
        name="grep_repomix_output",
        description=(
            "Search for patterns in a Repomix output file using grep-like functionality "
            "with JavaScript RegExp syntax. Supports context lines for better understanding of matches."
        ),
    )
    async def grep_repomix_output(input_data: GrepRepomixOutputInput) -> Dict[str, Any]:  # pyright: ignore[reportUnusedFunction]
        """Search for patterns in a repomix output file."""

        try:
            # Get file path from output ID
            file_path = get_output_file_path(input_data.output_id)
            if not file_path:
                return build_mcp_tool_error_response({"error_message": f"Output ID not found: {input_data.output_id}"})

            # Check if file exists
            path = Path(file_path)
            if not path.exists():
                return build_mcp_tool_error_response({"error_message": f"Output file not found: {file_path}"})

            # Read file content
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                return build_mcp_tool_error_response({"error_message": f"Failed to decode file as UTF-8: {file_path}"})

            # Compile regex pattern
            try:
                flags = re.IGNORECASE if input_data.ignore_case else 0
                regex = re.compile(input_data.pattern, flags)
            except re.error as e:
                return build_mcp_tool_error_response({"error_message": f"Invalid regex pattern: {e}"})

            # Determine context lines
            before_lines = input_data.before_lines if input_data.before_lines is not None else (input_data.context_lines or 0)
            after_lines = input_data.after_lines if input_data.after_lines is not None else (input_data.context_lines or 0)

            # Search for matches
            matches = []
            processed_lines = set()  # To avoid duplicate context lines

            for i, line in enumerate(lines):
                if regex.search(line):
                    # Calculate context range
                    start_line = max(0, i - before_lines)
                    end_line = min(len(lines), i + after_lines + 1)

                    # Collect context and mark processed lines
                    context_group = []
                    for j in range(start_line, end_line):
                        if j not in processed_lines:
                            line_num = j + 1
                            line_content = lines[j].rstrip("\n\r")
                            is_match = j == i

                            context_group.append(
                                {
                                    "line_number": line_num,
                                    "content": line_content,
                                    "is_match": is_match,
                                }
                            )
                            processed_lines.add(j)

                    if context_group:
                        matches.append({"match_line": i + 1, "context": context_group})

            # Format results
            if not matches:
                result_text = f"No matches found for pattern '{input_data.pattern}' in {path.name}"
            else:
                result_lines = [f"Found {len(matches)} match(es) for pattern '{input_data.pattern}' in {path.name}:\n"]

                for match_group in matches:
                    result_lines.append(f"--- Match at line {match_group['match_line']} ---")

                    for line_info in match_group["context"]:
                        line_num = line_info["line_number"]
                        content = line_info["content"]
                        is_match = line_info["is_match"]

                        # Mark matching lines with "> "
                        prefix = "> " if is_match else "  "
                        result_lines.append(f"{prefix}{line_num:4d}: {content}")

                    result_lines.append("")  # Empty line between match groups

                result_text = "\n".join(result_lines)

            return {"content": [{"type": "text", "text": result_text}]}

        except Exception as error:
            logger.error(f"Error in grep_repomix_output tool: {error}")
            return build_mcp_tool_error_response({"error_message": str(error)})
