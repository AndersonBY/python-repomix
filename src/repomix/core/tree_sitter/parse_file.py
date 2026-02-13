"""Main file parsing logic using tree-sitter for code compression."""

import logging
from pathlib import Path
from typing import List
import tree_sitter

from .ext2lang import get_language_from_extension
from .language_parser import language_parser

# Import strategies to register them
from .parse_strategies import python_parse_strategy  # noqa: F401 # pyright: ignore[reportUnusedImport]
from .parse_strategies import typescript_parse_strategy  # noqa: F401 # pyright: ignore[reportUnusedImport]
from .parse_strategies import go_parse_strategy  # noqa: F401 # pyright: ignore[reportUnusedImport]

logger = logging.getLogger(__name__)


def parse_file(content: str, file_path: str) -> str | None:
    """Parse a file using tree-sitter and return compressed content.

    Args:
        content: The file content to parse
        file_path: Path to the file (used for language detection)

    Returns:
        Compressed content if parsing successful, None if parsing failed
    """
    try:
        # Detect language from file extension
        file_extension = Path(file_path).suffix[1:]  # Remove the dot
        language = get_language_from_extension(file_extension)

        if language is None:
            logger.debug(f"Unsupported file extension: {file_extension}")
            return None

        # Check if language is supported by tree-sitter
        if not language_parser.is_language_supported(language):
            logger.debug(f"Tree-sitter language not available: {language}")
            return None

        # Get parser, query, and strategy
        parser = language_parser.get_parser(language)
        query = language_parser.get_query(language)
        strategy = language_parser.get_strategy(language)

        if parser is None:
            logger.debug(f"Parser not available for language: {language}")
            return None

        if query is None:
            logger.debug(f"Query not available for language: {language}")
            return None

        # Parse the content
        tree = parser.parse(content.encode("utf-8"))

        if tree.root_node.has_error:
            logger.debug(f"Parse error in file: {file_path}")
            return None

        # Execute the query using QueryCursor
        cursor = tree_sitter.QueryCursor(query)
        capture_dict = cursor.captures(tree.root_node)

        if not capture_dict:
            logger.debug(f"No captures found in file: {file_path}")
            return None

        # Convert the capture dictionary to the expected format
        captures = []
        for capture_name, nodes in capture_dict.items():
            for node in nodes:
                captures.append((node, capture_name))

        # Split content into lines for processing
        source_lines = content.splitlines()

        # Process captures using the strategy
        chunks = strategy.process_captures(captures, source_lines)

        if not chunks:
            logger.debug(f"No chunks extracted from file: {file_path}")
            return None

        # Sort chunks by line number
        chunks.sort(key=lambda c: c.start_line)

        # Join chunks with separator
        compressed_content = "\n⋮----\n".join(chunk.content for chunk in chunks)

        logger.debug(f"Successfully parsed {file_path}: {len(chunks)} chunks extracted")
        return compressed_content

    except Exception as e:
        logger.error(f"Error parsing file {file_path}: {e}")
        return None


def can_parse_file(file_path: str) -> bool:
    """Check if a file can be parsed with tree-sitter.

    Args:
        file_path: Path to the file

    Returns:
        True if file can be parsed, False otherwise
    """
    file_extension = Path(file_path).suffix[1:]  # Remove the dot
    language = get_language_from_extension(file_extension)

    if language is None:
        return False

    return language_parser.is_language_supported(language)


def get_supported_extensions() -> List[str]:
    """Get list of supported file extensions.

    Returns:
        List of supported file extensions (without dots)
    """
    from .ext2lang import ext2lang

    supported = []
    for ext, lang in ext2lang.items():
        if language_parser.is_language_supported(lang):
            supported.append(ext)

    return supported
