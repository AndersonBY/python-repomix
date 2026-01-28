"""Language to query mapping for tree-sitter queries."""

from typing import Dict, Optional

# Mapping of languages to their query module names
lang2query: Dict[str, str] = {
    "python": "query_python",
    "javascript": "query_javascript",
    "typescript": "query_typescript",
    "go": "query_go",
    "java": "query_java",
    "c": "query_c",
    "cpp": "query_cpp",
    "c_sharp": "query_csharp",
    "rust": "query_rust",
    "ruby": "query_ruby",
    "php": "query_php",
    "swift": "query_swift",
    "css": "query_css",
}


def get_query_module_name(language: str) -> Optional[str]:
    """Get the query module name for a given language.

    Args:
        language: Language name (e.g., 'python', 'javascript')

    Returns:
        Query module name if available, None otherwise
    """
    return lang2query.get(language)
