"""MCP tool runtime utilities for Repomix."""

import json
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...core.repo_processor import RepoProcessorResult

from ...shared.logger import logger


class McpToolError:
    """Error response for MCP tools."""
    
    def __init__(self, error_message: str, error_code: Optional[str] = None):
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
                "text": f"Error: {error_data.get('error_message', 'Unknown error occurred')}"
            }
        ],
        "isError": True
    }


def convert_error_to_json(error: Exception) -> Dict[str, Any]:
    """Convert an exception to a JSON-serializable format."""
    return {
        "error_message": str(error),
        "error_type": type(error).__name__
    }


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
    top_files_length: int = 10
) -> Dict[str, Any]:
    """Format the response for pack tools (pack_codebase and pack_remote_repository)."""
    
    try:
        # Generate unique output ID
        output_id = generate_output_id()
        
        # Read the generated output file to get some basic stats
        output_path = Path(output_file_path)
        if not output_path.exists():
            return build_mcp_tool_error_response({
                "error_message": f"Output file not found: {output_file_path}"
            })
        
        # Get file size and line count
        with open(output_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            line_count = len(content.splitlines())
        
        file_size = output_path.stat().st_size
        
        # Build response
        description = (
            f"Successfully packed {pack_result.total_files} files "
            f"into {output_file_path} ({file_size:,} bytes, {line_count:,} lines). "
            f"Total tokens: {pack_result.total_tokens:,}. "
            f"Use read_repomix_output with outputId '{output_id}' to access the content."
        )
        
        # Build detailed result JSON
        result_data = {
            "outputId": output_id,
            "outputFilePath": output_file_path,
            "totalFiles": pack_result.total_files,
            "totalTokens": pack_result.total_tokens,
            "totalCharacters": pack_result.total_chars,
            "totalSize": pack_result.total_chars,  # Using total_chars as size approximation
            "fileSize": file_size,
            "lineCount": line_count,
            "requestParams": request_params
        }
        
        # Store output file mapping for later retrieval
        _store_output_mapping(output_id, output_file_path)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "description": description,
                        "result": json.dumps(result_data),
                        "directoryStructure": str(pack_result.file_tree),
                        "outputId": output_id,
                        "outputFilePath": output_file_path,
                        "totalFiles": pack_result.total_files,
                        "totalTokens": pack_result.total_tokens
                    }, indent=2)
                }
            ]
        }
        
    except Exception as e:
        logger.error(f"Error formatting pack tool response: {e}")
        return build_mcp_tool_error_response(convert_error_to_json(e))


# Global storage for output ID to file path mapping
_output_mappings: Dict[str, str] = {}


def _store_output_mapping(output_id: str, file_path: str) -> None:
    """Store mapping between output ID and file path."""
    _output_mappings[output_id] = file_path
    logger.trace(f"Stored output mapping: {output_id} -> {file_path}")


def get_output_file_path(output_id: str) -> Optional[str]:
    """Get file path for a given output ID."""
    return _output_mappings.get(output_id)