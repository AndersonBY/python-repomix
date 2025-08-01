"""CLI types for MCP integration."""

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.repo_processor import RepoProcessorResult


@dataclass
class CliOptions:
    """CLI options for MCP tools."""

    compress: bool = False
    include: Optional[str] = None
    ignore: Optional[str] = None
    output: Optional[str] = None
    style: str = "xml"
    security_check: bool = True
    top_files_len: int = 10
    quiet: bool = False


@dataclass
class CliResult:
    """Result from CLI execution."""

    pack_result: "RepoProcessorResult"


# Create an alias for backward compatibility
PackResult = "RepoProcessorResult"
