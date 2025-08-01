"""Pack local codebase MCP tool."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from ...cli.cli_run import run_cli
from ...cli.types import CliOptions
from ...shared.logger import logger
from ..silent_mode import is_mcp_silent_mode
from .mcp_tool_runtime import (
    build_mcp_tool_error_response,
    convert_error_to_json,
    create_tool_workspace,
    format_pack_tool_response,
)


class PackCodebaseInput(BaseModel):
    """Input schema for pack_codebase tool."""

    directory: str = Field(description="Absolute path to the directory to pack")
    compress: bool = Field(
        default=False,
        description=(
            "Enable Tree-sitter compression to extract essential code signatures and structure "
            "while removing implementation details. Reduces token usage by ~70% while preserving semantic meaning. "
            "Generally not needed since grep_repomix_output allows incremental content retrieval. "
            "Use only when you specifically need the entire codebase content for large repositories."
        ),
    )
    include_patterns: Optional[str] = Field(
        default=None,
        description=(
            "Specify files to include using fast-glob patterns. Multiple patterns can be "
            'comma-separated (e.g., "**/*.{js,ts}", "src/**,docs/**"). Only matching files will be processed.'
        ),
    )
    ignore_patterns: Optional[str] = Field(
        default=None,
        description=(
            "Specify additional files to exclude using fast-glob patterns. Multiple patterns can be "
            'comma-separated (e.g., "test/**,*.spec.js", "node_modules/**,dist/**"). '
            "These patterns supplement .gitignore and built-in exclusions."
        ),
    )
    top_files_length: int = Field(
        default=10,
        description="Number of largest files by size to display in the metrics summary for codebase analysis",
    )


class PackCodebaseOutput(BaseModel):
    """Output schema for pack_codebase tool."""

    description: str = Field(description="Human-readable description of the packing results")
    result: str = Field(description="JSON string containing detailed metrics and file information")
    directory_structure: str = Field(description="Tree structure of the processed directory")
    output_id: str = Field(description="Unique identifier for accessing the packed content")
    output_file_path: str = Field(description="File path to the generated output file")
    total_files: int = Field(description="Total number of files processed")
    total_tokens: int = Field(description="Total token count of the content")


def register_pack_codebase_tool(server: FastMCP) -> None:
    """Register the pack_codebase tool with the MCP server."""

    @server.tool(
        name="pack_codebase",
        description=(
            "Package a local code directory into a consolidated XML file for AI analysis. "
            "This tool analyzes the codebase structure, extracts relevant code content, and generates "
            "a comprehensive report including metrics, file tree, and formatted code content. "
            "Supports Tree-sitter compression for efficient token usage."
        ),
    )
    async def pack_codebase(  # pyright: ignore[reportUnusedFunction]
        directory: str,
        compress: bool = False,
        include_patterns: Optional[str] = None,
        ignore_patterns: Optional[str] = None,
        top_files_length: int = 10,
    ) -> Dict[str, Any]:
        """Pack a local codebase into a consolidated XML file."""

        if not is_mcp_silent_mode():
            logger.log("🔨 MCP Tool Called: pack_codebase")
            logger.log(f"   📁 Directory: {directory}")
            logger.log(f"   🗜️ Compress: {compress}")
            logger.log(f"   📊 Top files: {top_files_length}")
            if include_patterns:
                logger.log(f"   ✅ Include: {include_patterns}")
            if ignore_patterns:
                logger.log(f"   ❌ Ignore: {ignore_patterns}")

        temp_dir = ""

        try:
            # Validate directory exists
            directory_path = Path(directory)

            if not directory_path.exists():
                error_msg = f"Directory does not exist: {directory}"
                if not is_mcp_silent_mode():
                    logger.warn(f"   ⚠️ {error_msg}")
                return build_mcp_tool_error_response({"error_message": error_msg})

            if not directory_path.is_dir():
                error_msg = f"Path is not a directory: {directory}"
                if not is_mcp_silent_mode():
                    logger.warn(f"   ⚠️ {error_msg}")
                return build_mcp_tool_error_response({"error_message": error_msg})

            if not is_mcp_silent_mode():
                logger.log("   🏗️ Creating workspace...")

            # Create temporary workspace
            temp_dir = await create_tool_workspace()
            output_file_path = os.path.join(temp_dir, "repomix-output.xml")

            if not is_mcp_silent_mode():
                logger.log(f"   📝 Output will be saved to: {output_file_path}")

            # Prepare CLI options
            cli_options = CliOptions(
                compress=compress,
                include=include_patterns,
                ignore=ignore_patterns,
                output=output_file_path,
                style="xml",
                security_check=True,
                top_files_len=top_files_length,
                quiet=True,
            )

            if not is_mcp_silent_mode():
                logger.log("   🔄 Processing repository...")

            # Run the CLI
            result = await run_cli([directory], str(directory_path.parent), cli_options)

            if not result:
                error_msg = "Failed to generate repomix output"
                if not is_mcp_silent_mode():
                    logger.error(f"   ❌ {error_msg}")
                return build_mcp_tool_error_response({"error_message": error_msg})

            if not is_mcp_silent_mode():
                logger.log("   ✅ Processing completed!")
                logger.log(f"   📊 Files processed: {result.pack_result.total_files}")
                logger.log(f"   📝 Characters: {result.pack_result.total_chars:,}")
                logger.log(f"   🎯 Tokens: {result.pack_result.total_tokens:,}")

            # Format response
            request_params = {
                "directory": directory,
                "compress": compress,
                "include_patterns": include_patterns,
                "ignore_patterns": ignore_patterns,
                "top_files_length": top_files_length,
            }

            # Format the response properly
            response = await format_pack_tool_response(request_params, result.pack_result, output_file_path, top_files_length)

            if not is_mcp_silent_mode():
                logger.log("   🎉 MCP response generated successfully")

            return response

        except Exception as error:
            if not is_mcp_silent_mode():
                logger.error(f"   ❌ Error in pack_codebase tool: {error}")
            return build_mcp_tool_error_response(convert_error_to_json(error))
