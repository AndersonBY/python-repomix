"""
Markdown Output Style Module - Implements Markdown Format Output
"""

from pathlib import Path
from typing import Dict, List

from ._utils import format_file_tree
from ...file.file_types import ProcessedFile
from ..output_style_decorate import OutputStyle


class MarkdownStyle(OutputStyle):
    """Markdown Output Style"""

    def generate_header(self) -> str:
        """Generate markdown format header"""
        if self.config.output.header_text:
            header_text = f"User Provided Header:\n-----------------------\n{self.config.output.header_text}\n\n"
        else:
            header_text = ""
        return (
            f"{self.header}\n\n"
            f"# File Summary\n\n"
            "## Purpose:\n\n"
            f"{self.summary_purpose}\n\n"
            "## File Format:\n\n"
            f"{self.summary_file_format}\n"
            "4. Multiple file entries, each consisting of:\n"
            "   a. A header with the file path (## File: path/to/file)\n"
            "   b. The full contents of the file in a code block\n\n"
            "## Usage Guidelines:\n\n"
            f"{self.summary_usage_guidelines}\n\n"
            "## Notes:\n\n"
            f"{self.summary_notes}\n\n"
            "## Additional Information:\n\n"
            f"{header_text}"
            f"{self.summary_additional_info}\n\n"
        )

    def generate_footer(self) -> str:
        """Generate Markdown format footer

        Returns:
            Markdown footer content
        """
        return ""

    def generate_files_section(
        self,
        files: List[ProcessedFile],
        file_char_counts: Dict[str, int],
        file_token_counts: Dict[str, int],
    ) -> str:
        """Generate plain text format files section

        Args:
            files: List of processed files

        Returns:
            Plain text format files section content
        """
        # Initialize empty output string
        output = "# Repository Files\n\n"

        # Generate section for each file
        for file in files:
            output += self.generate_file_section(
                file_path=file.path,
                content=file.content,
                char_count=file_char_counts.get(file.path, 0),
                token_count=file_token_counts.get(file.path, 0),
            )

        return output

    def generate_file_section(self, file_path: str, content: str, char_count: int, token_count: int) -> str:
        """Generate Markdown format file section

        Args:
            file_path: File path
            content: File content
            char_count: Character count
            token_count: Token count

        Returns:
            Markdown format file section content
        """
        # Get file extension to determine language
        ext = Path(file_path).suffix
        language = self._get_language_by_extension(ext)

        # Generate file information
        section = f"\n## {file_path}\n\n"
        section += f"- Characters: {char_count}\n"
        section += f"- Tokens: {token_count}\n\n"

        # Add code block
        section += f"```{language}\n"
        section += content
        section += "\n```\n"

        return section

    def generate_statistics(self, total_files: int, total_chars: int, total_tokens: int) -> str:
        """Generate Markdown format statistics

        Args:
            total_files: Total number of files
            total_chars: Total character count
            total_tokens: Total token count

        Returns:
            Markdown format statistics content
        """
        stats = "\n## Statistics\n\n"
        stats += f"- Total Files: {total_files}\n"
        stats += f"- Total Characters: {total_chars}\n"
        stats += f"- Total Tokens: {total_tokens}\n"
        return stats

    def generate_file_tree_section(self, file_tree: Dict) -> str:
        """Generates the file tree section in Markdown style."""
        return "\n# Repository Structure\n\n```\n" + format_file_tree(file_tree) + "```\n\n"

    def _get_language_by_extension(self, ext: str) -> str:
        """Get language identifier by file extension

        Args:
            ext: File extension

        Returns:
            Language identifier
        """
        # Extension to language mapping
        language_map: Dict[str, str] = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".html": "html",
            ".css": "css",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
            ".sh": "bash",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".xml": "xml",
            ".md": "markdown",
            ".sql": "sql",
        }

        return language_map.get(ext.lower(), "text")
