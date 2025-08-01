"""File extension to language mapping for tree-sitter parsers."""

from typing import Dict

# Mapping of file extensions to supported languages
ext2lang: Dict[str, str] = {
    # Python
    "py": "python",
    "pyi": "python",
    "pyx": "python",
    # JavaScript/TypeScript
    "js": "javascript",
    "jsx": "javascript",
    "ts": "typescript",
    "tsx": "typescript",
    "mjs": "javascript",
    "cjs": "javascript",
    # Go
    "go": "go",
    # C/C++
    "c": "c",
    "h": "c",
    "cpp": "cpp",
    "cc": "cpp",
    "cxx": "cpp",
    "hpp": "cpp",
    "hxx": "cpp",
    # Java
    "java": "java",
    # C#
    "cs": "c_sharp",
    # Rust
    "rs": "rust",
    # Ruby
    "rb": "ruby",
    # PHP
    "php": "php",
    # Swift
    "swift": "swift",
    # Kotlin
    "kt": "kotlin",
    "kts": "kotlin",
    # Scala
    "scala": "scala",
    "sc": "scala",
    # Bash/Shell
    "sh": "bash",
    "bash": "bash",
    "zsh": "bash",
    # HTML/CSS
    "html": "html",
    "htm": "html",
    "css": "css",
    # JSON/YAML
    "json": "json",
    "yaml": "yaml",
    "yml": "yaml",
    # SQL
    "sql": "sql",
    # Lua
    "lua": "lua",
    # R
    "r": "r",
    "R": "r",
    # Haskell
    "hs": "haskell",
    # OCaml
    "ml": "ocaml",
    "mli": "ocaml",
    # Elixir
    "ex": "elixir",
    "exs": "elixir",
}


def get_language_from_extension(file_extension: str) -> str | None:
    """Get the language name from a file extension.

    Args:
        file_extension: File extension without the dot (e.g., 'py', 'js')

    Returns:
        Language name if supported, None otherwise
    """
    return ext2lang.get(file_extension.lower())


def is_supported_language(file_extension: str) -> bool:
    """Check if a file extension is supported by tree-sitter.

    Args:
        file_extension: File extension without the dot

    Returns:
        True if the language is supported, False otherwise
    """
    return file_extension.lower() in ext2lang
