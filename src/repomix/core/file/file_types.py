"""
File Types Module - Contains data classes used for file processing
"""

from dataclasses import dataclass


@dataclass
class RawFile:
    """Raw File Class

    Attributes:
        path: File path
        content: File content
    """

    path: str
    content: str


@dataclass
class ProcessedFile:
    """Processed File Class

    Attributes:
        path: File path
        content: Processed file content
    """

    path: str
    content: str


@dataclass
class FileStats:
    """File Statistics Class

    Attributes:
        char_count: Character count
        token_count: Token count
        line_count: Line count
    """

    char_count: int
    token_count: int
    line_count: int
