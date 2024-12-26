"""
Plain Text Output Style Module - Implements Plain Text Format Output
"""

from typing import Dict, List

from ._utils import format_file_tree
from ..output_style_decorate import OutputStyle
from ....core.file.file_types import ProcessedFile


PLAIN_LONG_SEPARATOR = "=" * 64
PLAIN_SHORT_SEPARATOR = "=" * 16


class PlainStyle(OutputStyle):
    """Plain Text Output Style"""

    def generate_header(self) -> str:
        """Generate plain text format header"""
        if self.config.output.header_text:
            header_text = f"User Provided Header:\n-----------------------\n{self.config.output.header_text}\n\n"
        else:
            header_text = ""
        return (
            f"{self.header}\n\n"
            f"{PLAIN_LONG_SEPARATOR}\n"
            f"File Summary\n"
            f"{PLAIN_LONG_SEPARATOR}\n\n"
            "Purpose:\n"
            "--------\n"
            f"{self.summary_purpose}\n\n"
            "File Format:\n"
            "------------\n"
            f"{self.summary_file_format}\n"
            "4. Multiple file entries, each consisting of:\n"
            "   a. A separator line (================)\n"
            "   b. The file path (File: path/to/file)\n"
            "   c. Another separator line\n"
            "   d. The full contents of the file\n"
            "   e. A blank line\n\n"
            "Usage Guidelines:\n"
            "------------------\n"
            f"{self.summary_usage_guidelines}\n\n"
            "Notes:\n"
            "------\n"
            f"{self.summary_notes}\n\n"
            "Additional Information:\n"
            "------------------------\n"
            f"{header_text}"
            f"{self.summary_additional_info}\n\n"
        )

    def generate_footer(self) -> str:
        """Generate plain text format footer"""
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
        output = PLAIN_LONG_SEPARATOR + "\nRepository Files\n" + PLAIN_LONG_SEPARATOR + "\n"

        # Generate section for each file
        for file in files:
            output += self.generate_file_section(
                file_path=file.path,
                content=file.content,
                char_count=file_char_counts.get(file.path, 0),
                token_count=file_token_counts.get(file.path, 0),
            )

        return f"{output}\n\n"

    def generate_file_section(self, file_path: str, content: str, char_count: int, token_count: int) -> str:
        """Generate plain text format file section"""
        # Create file header with equal signs
        section = "\n" + PLAIN_SHORT_SEPARATOR + "\n"
        section += f"File: {file_path}\n"
        section += PLAIN_SHORT_SEPARATOR + "\n"
        # Add file content
        section += f"{content}\n"
        return section

    def generate_statistics(self, total_files: int, total_chars: int, total_tokens: int) -> str:
        """Generate plain text format statistics

        Args:
            total_files: Total number of files
            total_chars: Total character count
            total_tokens: Total token count

        Returns:
            Plain text format statistics content
        """
        stats = f"{PLAIN_LONG_SEPARATOR}\n"
        stats += "Statistics\n"
        stats += f"{PLAIN_LONG_SEPARATOR}\n"
        stats += f"Total Files: {total_files}\n"
        stats += f"Total Characters: {total_chars}\n"
        stats += f"Total Tokens: {total_tokens}\n"
        return stats

    def generate_file_tree_section(self, file_tree: Dict) -> str:
        """Generates the file tree section in plain text style."""
        return (
            f"{PLAIN_LONG_SEPARATOR}\nRepository Structure:\n{PLAIN_LONG_SEPARATOR}\n"
            + format_file_tree(file_tree)
            + "\n"
        )

    def _get_current_time(self) -> str:
        """Get formatted current time string

        Returns:
            Formatted time string
        """
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
