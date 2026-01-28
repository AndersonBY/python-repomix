"""
JSON Output Style Module - Implements JSON Format Output
"""

import json
from typing import Dict, List, Any

from ._utils import format_file_tree
from ...file.file_types import ProcessedFile
from ..output_style_decorate import OutputStyle


class JsonStyle(OutputStyle):
    """JSON Output Style"""

    def generate_header(self) -> str:
        """Generate JSON format header - not used directly in JSON output"""
        return ""

    def generate_footer(self) -> str:
        """Generate JSON format footer - not used directly in JSON output"""
        return ""

    def generate_files_section(
        self,
        files: List[ProcessedFile],
        file_char_counts: Dict[str, int],
        file_token_counts: Dict[str, int],
    ) -> str:
        """Generate JSON format files section - not used directly"""
        return ""

    def generate_file_section(
        self, file_path: str, content: str, char_count: int, token_count: int
    ) -> str:
        """Generate JSON format file section - not used directly"""
        return ""

    def generate_statistics(
        self, total_files: int, total_chars: int, total_tokens: int
    ) -> str:
        """Generate JSON format statistics - not used directly"""
        return ""

    def generate_file_tree_section(self, file_tree: Dict) -> str:
        """Generate JSON format file tree section - not used directly"""
        return ""

    def generate_json_output(
        self,
        files: List[ProcessedFile],
        file_char_counts: Dict[str, int],
        file_token_counts: Dict[str, int],
        file_tree: Dict,
        total_files: int,
        total_chars: int,
        total_tokens: int,
    ) -> str:
        """Generate complete JSON output

        Args:
            files: List of processed files
            file_char_counts: File character count statistics
            file_token_counts: File token count statistics
            file_tree: File tree structure
            total_files: Total number of files
            total_chars: Total character count
            total_tokens: Total token count

        Returns:
            JSON formatted output string
        """
        json_document: Dict[str, Any] = {}

        # Add file summary section
        json_document["fileSummary"] = {
            "generationHeader": self.header,
            "purpose": self.summary_purpose,
            "fileFormat": self._get_file_format_description(),
            "usageGuidelines": self.summary_usage_guidelines,
            "notes": self.summary_notes,
        }

        # Add user provided header if exists
        if self.config.output.header_text:
            json_document["userProvidedHeader"] = self.config.output.header_text

        # Add directory structure if enabled
        if self.config.output.show_directory_structure:
            json_document["directoryStructure"] = format_file_tree(file_tree)

        # Add files section
        json_document["files"] = {}
        for file in files:
            file_entry: Dict[str, Any] = {"content": file.content}

            # Add file stats if configured
            if self.config.output.show_file_stats:
                file_entry["charCount"] = file_char_counts.get(file.path, 0)
                file_entry["tokenCount"] = file_token_counts.get(file.path, 0)

            json_document["files"][file.path] = file_entry

        # Add statistics
        json_document["statistics"] = {
            "totalFiles": total_files,
            "totalCharacters": total_chars,
            "totalTokens": total_tokens,
        }

        return json.dumps(json_document, indent=2, ensure_ascii=False)

    def _get_file_format_description(self) -> str:
        """Get file format description for JSON output"""
        return (
            "The content is organized as a JSON object with the following structure:\n"
            "1. fileSummary: Contains metadata about this file\n"
            "2. directoryStructure: Text representation of the repository structure\n"
            "3. files: Object mapping file paths to their contents\n"
            "4. statistics: Summary statistics about the repository"
        )
