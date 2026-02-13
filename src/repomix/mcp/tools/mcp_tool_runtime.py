"""MCP tool runtime utilities for Repomix."""

import json
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.repo_processor import RepoProcessorResult

from ...shared.logger import logger


class McpToolError:
    """Error response for MCP tools."""

    def __init__(self, error_message: str, error_code: str | None = None):
        self.error_message = error_message
        self.error_code = error_code

    def to_dict(self) -> Dict[str, Any]:
        result = {"error_message": self.error_message}
        if self.error_code:
            result["error_code"] = self.error_code
        return result


def build_mcp_tool_error_response(error_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build a standardized error response for MCP tools."""
    return {
        "content": [
            {
                "type": "text",
                "text": f"Error: {error_data.get('error_message', 'Unknown error occurred')}",
            }
        ],
        "isError": True,
    }


def convert_error_to_json(error: Exception) -> Dict[str, Any]:
    """Convert an exception to a JSON-serializable format."""
    return {"error_message": str(error), "error_type": type(error).__name__}


async def create_tool_workspace() -> str:
    """Create a temporary workspace directory for MCP tools."""
    temp_dir = tempfile.mkdtemp(prefix="repomix_mcp_")
    logger.trace(f"Created MCP tool workspace: {temp_dir}")
    return temp_dir


def generate_output_id() -> str:
    """Generate a unique output ID for tracking repomix outputs."""
    return str(uuid.uuid4())


async def format_pack_tool_response(
    request_params: Dict[str, Any],
    pack_result: "RepoProcessorResult",
    output_file_path: str,
    top_files_length: int = 10,
) -> Dict[str, Any]:
    """Format the response for pack tools (pack_codebase and pack_remote_repository)."""

    try:
        # Generate unique output ID
        output_id = generate_output_id()

        # Read the generated output file to get some basic stats
        output_path = Path(output_file_path)

        if not output_path.exists():
            return build_mcp_tool_error_response({"error_message": f"Output file not found: {output_file_path}"})

        file_size = output_path.stat().st_size

        # Get line count more efficiently without reading entire file into memory
        line_count = 0
        with open(output_file_path, "rb") as f:
            for _ in f:
                line_count += 1

        # Build response
        description = (
            f"Successfully packed {pack_result.total_files} files "
            f"into {output_file_path} ({file_size:,} bytes, {line_count:,} lines). "
            f"Total tokens: {pack_result.total_tokens:,}. "
            f"Use read_repomix_output with outputId '{output_id}' to access the content."
        )

        # Store output file mapping for later retrieval
        _store_output_mapping(output_id, output_file_path)

        # Convert file_tree to string carefully
        try:
            directory_structure = json.dumps(pack_result.file_tree) if isinstance(pack_result.file_tree, dict) else str(pack_result.file_tree)
        except Exception:
            directory_structure = "Error: Could not serialize directory structure"

        # Create a simplified response structure
        response_text = f"""{description}

Output Details:
- Output ID: {output_id}
- Output File: {output_file_path}
- Total Files: {pack_result.total_files}
- Total Tokens: {pack_result.total_tokens:,}
- Total Characters: {pack_result.total_chars:,}
- File Size: {file_size:,} bytes
- Line Count: {line_count:,}

Directory Structure:
{directory_structure[:1000]}{"... (truncated)" if len(directory_structure) > 1000 else ""}

Use 'read_repomix_output' with outputId '{output_id}' to access the full content."""

        response = {"content": [{"type": "text", "text": response_text}]}

        return response

    except Exception as e:
        logger.error(f"Error formatting pack tool response: {e}")
        return build_mcp_tool_error_response(convert_error_to_json(e))


# Global storage for output ID to file path mapping
_output_mappings: Dict[str, str] = {}


def _store_output_mapping(output_id: str, file_path: str) -> None:
    """Store mapping between output ID and file path."""
    _output_mappings[output_id] = file_path
    logger.trace(f"Stored output mapping: {output_id} -> {file_path}")


def get_output_file_path(output_id: str) -> str | None:
    """Get file path for a given output ID."""
    return _output_mappings.get(output_id)
