"""
File Manipulation Module - Provides Various Methods for File Content Operations
"""

import re
from typing import Dict
from pathlib import Path


class FileManipulator:
    """Base File Manipulator Class"""

    def remove_comments(self, content: str) -> str:
        """Remove comments

        Args:
            content: File content

        Returns:
            Content with comments removed
        """
        return content

    def remove_empty_lines(self, content: str) -> str:
        """Remove empty lines

        Args:
            content: File content

        Returns:
            Content with empty lines removed
        """
        return "\n".join(line for line in content.splitlines() if line.strip())


class StripCommentsManipulator(FileManipulator):
    """Generic Comment Remover"""

    def __init__(self, language: str):
        """Initialize

        Args:
            language: Programming language name
        """
        super().__init__()
        self.language = language

    def remove_comments(self, content: str) -> str:
        """Remove comments based on language type

        Args:
            content: File content

        Returns:
            Content with comments removed
        """
        if self.language == "python":
            return self._remove_python_comments(content)
        elif self.language == "html":
            return self._remove_html_comments(content)
        else:
            return self._remove_generic_comments(content)

    def _remove_generic_comments(self, content: str) -> str:
        """Remove comments in generic format (C-style)"""
        # Remove single-line comments
        content = re.sub(r"//.*", "", content)
        # Remove multi-line comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
        return content

    def _remove_html_comments(self, content: str) -> str:
        """Remove HTML comments"""
        return re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)

    def _remove_python_comments(self, content: str) -> str:
        """Remove Python comments"""
        # Remove single-line comments
        content = re.sub(r"#.*", "", content)
        # Remove docstrings
        content = re.sub(r'""".*?"""', "", content, flags=re.DOTALL)
        content = re.sub(r"'''.*?'''", "", content, flags=re.DOTALL)
        return content


class PythonManipulator(FileManipulator):
    """Python-specific File Manipulator"""

    def remove_comments(self, content: str) -> str:
        """Remove Python comments and docstrings"""
        # Remove docstrings
        content = re.sub(r'""".*?"""', "", content, flags=re.DOTALL)
        content = re.sub(r"'''.*?'''", "", content, flags=re.DOTALL)
        # Remove single-line comments
        content = re.sub(r"#.*", "", content)
        return content


class CompositeManipulator(FileManipulator):
    """Composite File Manipulator for handling multi-language mixed files (like Vue)"""

    def __init__(self, *manipulators: FileManipulator):
        """Initialize

        Args:
            *manipulators: Multiple file manipulator instances
        """
        super().__init__()
        self.manipulators = manipulators

    def remove_comments(self, content: str) -> str:
        """Process content using all manipulators"""
        for manipulator in self.manipulators:
            content = manipulator.remove_comments(content)
        return content


# Mapping of file extensions to manipulators
manipulators: Dict[str, FileManipulator] = {
    # Common programming languages
    ".py": PythonManipulator(),
    ".js": StripCommentsManipulator("javascript"),
    ".ts": StripCommentsManipulator("javascript"),
    ".java": StripCommentsManipulator("java"),
    ".c": StripCommentsManipulator("c"),
    ".cpp": StripCommentsManipulator("c"),
    ".cs": StripCommentsManipulator("csharp"),
    # Web-related
    ".html": StripCommentsManipulator("html"),
    ".css": StripCommentsManipulator("css"),
    ".jsx": StripCommentsManipulator("javascript"),
    ".tsx": StripCommentsManipulator("javascript"),
    ".vue": CompositeManipulator(
        StripCommentsManipulator("html"),
        StripCommentsManipulator("css"),
        StripCommentsManipulator("javascript"),
    ),
    ".svelte": CompositeManipulator(
        StripCommentsManipulator("html"),
        StripCommentsManipulator("css"),
        StripCommentsManipulator("javascript"),
    ),
    # Other languages
    ".go": StripCommentsManipulator("c"),
    ".rb": StripCommentsManipulator("ruby"),
    ".php": StripCommentsManipulator("php"),
    ".swift": StripCommentsManipulator("swift"),
    ".kt": StripCommentsManipulator("c"),
    ".rs": StripCommentsManipulator("c"),
    # Configuration files
    ".xml": StripCommentsManipulator("xml"),
    ".yaml": StripCommentsManipulator("perl"),
    ".yml": StripCommentsManipulator("perl"),
}


def get_file_manipulator(file_path: str | Path) -> FileManipulator | None:
    """Get the corresponding file manipulator based on file extension

    Args:
        file_path: File path (string or Path object)

    Returns:
        Corresponding file manipulator instance, or None if no matching manipulator
    """
    ext = Path(file_path).suffix
    return manipulators.get(ext)
