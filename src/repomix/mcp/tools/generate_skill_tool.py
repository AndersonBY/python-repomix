"""Generate skill MCP tool - Creates Claude Agent Skills from codebase."""

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
)


class GenerateSkillInput(BaseModel):
    """Input schema for generate_skill tool."""

    directory: str = Field(description="Absolute path to the directory to generate skill from")
    skill_name: Optional[str] = Field(
        default=None,
        description="Name for the generated skill. If not provided, uses directory name.",
    )
    include_patterns: Optional[str] = Field(
        default=None,
        description=('Specify files to include using fast-glob patterns. Multiple patterns can be comma-separated (e.g., "**/*.{js,ts}", "src/**,docs/**").'),
    )
    ignore_patterns: Optional[str] = Field(
        default=None,
        description=('Specify additional files to exclude using fast-glob patterns. Multiple patterns can be comma-separated (e.g., "test/**,*.spec.js").'),
    )


class GenerateSkillOutput(BaseModel):
    """Output schema for generate_skill tool."""

    description: str = Field(description="Human-readable description of the skill generation results")
    skill_name: str = Field(description="Name of the generated skill")
    output_directory: str = Field(description="Directory where skill files were generated")
    files_generated: list = Field(description="List of generated skill files")
    total_files: int = Field(description="Total number of source files included")
    total_lines: int = Field(description="Total lines of code")


def register_generate_skill_tool(server: FastMCP) -> None:
    """Register the generate_skill tool with the MCP server."""

    @server.tool(
        name="generate_skill",
        description=(
            "Generate a Claude Agent Skill from a local codebase. "
            "Creates a skill package with SKILL.md, summary, project structure, "
            "and file contents that can be used as a reference skill in Claude."
        ),
    )
    async def generate_skill(  # pyright: ignore[reportUnusedFunction]
        directory: str,
        skill_name: Optional[str] = None,
        include_patterns: Optional[str] = None,
        ignore_patterns: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a Claude Agent Skill from a codebase."""

        if not is_mcp_silent_mode():
            logger.log("🔨 MCP Tool Called: generate_skill")
            logger.log(f"   📁 Directory: {directory}")
            if skill_name:
                logger.log(f"   📛 Skill name: {skill_name}")
            if include_patterns:
                logger.log(f"   ✅ Include: {include_patterns}")
            if ignore_patterns:
                logger.log(f"   ❌ Ignore: {ignore_patterns}")

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

            # Create temporary workspace for skill output
            temp_dir = await create_tool_workspace()
            skill_output_dir = os.path.join(temp_dir, "skill")
            os.makedirs(skill_output_dir, exist_ok=True)

            if not is_mcp_silent_mode():
                logger.log(f"   📝 Skill will be saved to: {skill_output_dir}")

            # Determine skill name
            actual_skill_name = skill_name if skill_name else directory_path.name

            # Prepare CLI options for skill generation
            cli_options = CliOptions(
                include=include_patterns,
                ignore=ignore_patterns,
                output=os.path.join(skill_output_dir, "SKILL.md"),
                style="markdown",
                security_check=True,
                quiet=True,
            )

            if not is_mcp_silent_mode():
                logger.log("   🔄 Processing repository for skill generation...")

            # Run the CLI to process the codebase
            result = await run_cli([directory], str(directory_path.parent), cli_options)

            if not result:
                error_msg = "Failed to generate skill output"
                if not is_mcp_silent_mode():
                    logger.error(f"   ❌ {error_msg}")
                return build_mcp_tool_error_response({"error_message": error_msg})

            # List generated files
            generated_files = []
            for root, _dirs, files in os.walk(skill_output_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), skill_output_dir)
                    generated_files.append(rel_path)

            if not is_mcp_silent_mode():
                logger.log("   ✅ Skill generation completed!")
                logger.log(f"   📊 Files processed: {result.pack_result.total_files}")
                logger.log(f"   📝 Generated files: {len(generated_files)}")

            # Calculate total lines from file char counts (approximate)
            total_lines = sum(result.pack_result.file_char_counts.values()) // 40 if result.pack_result.file_char_counts else 0

            # Build response
            response = {
                "description": f"Successfully generated skill '{actual_skill_name}' from {directory}",
                "skill_name": actual_skill_name,
                "output_directory": skill_output_dir,
                "files_generated": generated_files,
                "total_files": result.pack_result.total_files,
                "total_lines": total_lines,
            }

            if not is_mcp_silent_mode():
                logger.log("   🎉 MCP response generated successfully")

            return response

        except Exception as error:
            if not is_mcp_silent_mode():
                logger.error(f"   ❌ Error in generate_skill tool: {error}")
            return build_mcp_tool_error_response(convert_error_to_json(error))
