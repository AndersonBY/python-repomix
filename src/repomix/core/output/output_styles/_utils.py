"""
Utils for output styles
"""

from typing import Dict


def format_file_tree(tree: Dict, indent: int = 0) -> str:
    """
    Formats the file tree as a string.

    Args:
        tree: The file tree dictionary.
        indent: The current indentation level.

    Returns:
        The formatted string representation of the tree.
    """
    tree_str = ""
    for name, content in tree.items():
        tree_str += "  " * indent + name + "\n"
        if isinstance(content, dict):  # Directory
            tree_str += format_file_tree(content, indent + 1)
    return tree_str
