"""
XML Output Style Module - Implements XML Format Output
"""

from xml.dom import minidom
from typing import Dict, List
import xml.etree.ElementTree as ET

from ..output_style_decorate import OutputStyle
from ....core.file.file_types import ProcessedFile


class XmlStyle(OutputStyle):
    """XML Output Style"""

    def generate_header(self) -> str:
        """Generate XML format header

        Returns:
            XML format header content
        """
        return '<?xml version="1.0" encoding="UTF-8"?>\n<repository>\n'

    def generate_footer(self) -> str:
        """Generate XML format footer

        Returns:
            XML format footer content
        """
        return "</repository>"

    def generate_files_section(
        self,
        files: List[ProcessedFile],
        file_char_counts: Dict[str, int],
        file_token_counts: Dict[str, int],
    ) -> str:
        """Generate XML format files section

        Args:
            files: List of processed files
            file_char_counts: Dictionary of character counts per file
            file_token_counts: Dictionary of token counts per file

        Returns:
            XML format files section content
        """
        # Create root element for files section
        files_elem = ET.Element("repository_files")

        # Generate section for each file
        for file in files:
            file_content = self.generate_file_section(
                file_path=file.path,
                content=file.content,
                char_count=file_char_counts.get(file.path, 0),
                token_count=file_token_counts.get(file.path, 0),
            )
            # Parse the file content back to XML and append to files element
            file_xml = ET.fromstring(file_content)
            files_elem.append(file_xml)

        # Convert to string and format
        xml_str = ET.tostring(files_elem, encoding="unicode")
        return self._pretty_print(xml_str)

    def generate_file_section(self, file_path: str, content: str, char_count: int, token_count: int) -> str:
        """Generate XML format file section

        Args:
            file_path: File path
            content: File content
            char_count: Character count
            token_count: Token count

        Returns:
            XML format file section content
        """
        # Create file element
        file_elem = ET.Element("file")

        # Add file attributes
        path_elem = ET.SubElement(file_elem, "path")
        path_elem.text = file_path

        stats_elem = ET.SubElement(file_elem, "stats")
        chars_elem = ET.SubElement(stats_elem, "chars")
        chars_elem.text = str(char_count)
        tokens_elem = ET.SubElement(stats_elem, "tokens")
        tokens_elem.text = str(token_count)

        # Add file content
        content_elem = ET.SubElement(file_elem, "content")
        content_elem.text = content

        # Convert to string and format
        xml_str = ET.tostring(file_elem, encoding="unicode")
        pretty_xml = self._pretty_print(xml_str)

        return pretty_xml

    def generate_statistics(self, total_files: int, total_chars: int, total_tokens: int) -> str:
        """Generate XML format statistics

        Args:
            total_files: Total number of files
            total_chars: Total character count
            total_tokens: Total token count

        Returns:
            XML format statistics content
        """
        # Create statistics element
        stats_elem = ET.Element("statistics")

        # Add statistics data
        files_elem = ET.SubElement(stats_elem, "total_files")
        files_elem.text = str(total_files)

        chars_elem = ET.SubElement(stats_elem, "total_chars")
        chars_elem.text = str(total_chars)

        tokens_elem = ET.SubElement(stats_elem, "total_tokens")
        tokens_elem.text = str(total_tokens)

        # Add generation time
        time_elem = ET.SubElement(stats_elem, "generated_at")
        time_elem.text = self._get_current_time()

        # Convert to string and format
        xml_str = ET.tostring(stats_elem, encoding="unicode")
        pretty_xml = self._pretty_print(xml_str)

        return pretty_xml

    def _format_file_tree_xml(self, tree: Dict, parent: ET.Element) -> None:
        """Recursively formats the file tree for XML output."""
        for name, content in tree.items():
            if isinstance(content, dict):
                dir_elem = ET.SubElement(parent, "directory")
                dir_elem.set("name", name)
                self._format_file_tree_xml(content, dir_elem)
            else:
                file_elem = ET.SubElement(parent, "file")
                file_elem.set("name", name)

    def generate_file_tree_section(self, file_tree: Dict) -> str:
        """Generates the file tree section in XML style."""
        tree_elem = ET.Element("repository_structure")
        self._format_file_tree_xml(file_tree, tree_elem)
        xml_str = ET.tostring(tree_elem, encoding="unicode")
        return self._pretty_print(xml_str)

    def _pretty_print(self, xml_str: str) -> str:
        """Pretty print XML output

        Args:
            xml_str: Original XML string

        Returns:
            Formatted XML string
        """
        parsed = minidom.parseString(xml_str)
        return parsed.toprettyxml(indent="  ").split("\n", 1)[1]

    def _get_current_time(self) -> str:
        """Get formatted current time string

        Returns:
            Formatted time string
        """
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
