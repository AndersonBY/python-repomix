"""
Token Count Tree Module - Builds and displays token count tree structure
"""

from dataclasses import dataclass
from typing import Dict, List

from ...config.config_schema import RepomixConfig
from ..file.file_types import ProcessedFile


@dataclass
class FileTokenInfo:
    """Token information for a single file"""

    name: str
    tokens: int


@dataclass
class FileWithTokens:
    """File path with token count"""

    path: str
    tokens: int


class TreeNode:
    """Tree node for token count structure"""

    def __init__(self):
        self.files: List[FileTokenInfo] = []
        self.token_sum: int = 0
        self.children: Dict[str, TreeNode] = {}


def build_token_count_tree(files_with_tokens: List[FileWithTokens]) -> TreeNode:
    """Build a tree structure with token counts

    Args:
        files_with_tokens: List of files with their token counts

    Returns:
        Root TreeNode with the complete structure
    """
    root = TreeNode()

    for file in files_with_tokens:
        if not file.path or not isinstance(file.path, str):
            continue

        # Always use forward slash for consistency across platforms
        parts = file.path.replace("\\", "/").split("/")
        file_name = parts.pop() if parts else file.path
        if not file_name:
            continue

        # Navigate/create the directory structure
        current = root
        for part in parts:
            if part not in current.children:
                current.children[part] = TreeNode()
            current = current.children[part]

        # Add the file
        current.files.append(FileTokenInfo(name=file_name, tokens=file.tokens))

    # Calculate token sums for each directory
    _calculate_token_sums(root)

    return root


def _calculate_token_sums(node: TreeNode) -> int:
    """Calculate token sums for a node and all its children

    Args:
        node: TreeNode to calculate sums for

    Returns:
        Total token count for this node and all children
    """
    total_tokens = 0

    # Add tokens from files in this directory
    total_tokens += sum(f.tokens for f in node.files)

    # Add tokens from subdirectories
    for child in node.children.values():
        total_tokens += _calculate_token_sums(child)

    node.token_sum = total_tokens
    return total_tokens


def format_token_count_tree(
    node: TreeNode,
    min_token_count: int = 0,
    prefix: str = "",
    is_root: bool = True,
) -> str:
    """Format token count tree as a string

    Args:
        node: TreeNode to format
        min_token_count: Minimum token count to display
        prefix: Prefix for indentation
        is_root: Whether this is the root node

    Returns:
        Formatted string representation of the tree
    """
    lines: List[str] = []

    # Get directories filtered by minimum token count
    entries = [(name, child) for name, child in node.children.items() if child.token_sum >= min_token_count]

    # Get files filtered by minimum token count
    files = [f for f in node.files if f.tokens >= min_token_count]

    # Sort entries alphabetically
    entries.sort(key=lambda x: x[0])
    files.sort(key=lambda x: x.name)

    # Display files first
    for i, file in enumerate(files):
        is_last_file = i == len(files) - 1 and len(entries) == 0
        connector = "└── " if is_last_file else "├── "
        token_info = f"({file.tokens:,} tokens)"

        if is_root and prefix == "":
            lines.append(f"{connector}{file.name} {token_info}")
        else:
            lines.append(f"{prefix}{connector}{file.name} {token_info}")

    # Display directories
    for i, (name, child_node) in enumerate(entries):
        is_last_entry = i == len(entries) - 1
        connector = "└── " if is_last_entry else "├── "
        token_info = f"({child_node.token_sum:,} tokens)"

        if is_root and prefix == "":
            lines.append(f"{connector}{name}/ {token_info}")
        else:
            lines.append(f"{prefix}{connector}{name}/ {token_info}")

        # Prepare prefix for children
        if is_root and prefix == "":
            child_prefix = "    " if is_last_entry else "│   "
        else:
            child_prefix = prefix + ("    " if is_last_entry else "│   ")

        child_output = format_token_count_tree(child_node, min_token_count, child_prefix, False)
        if child_output:
            lines.append(child_output)

    # If this is the root and it's empty, show a message
    if is_root and len(files) == 0 and len(entries) == 0:
        if min_token_count > 0:
            lines.append(f"No files or directories found with {min_token_count}+ tokens.")
        else:
            lines.append("No files found.")

    return "\n".join(lines)


def report_token_count_tree(
    processed_files: List[ProcessedFile],
    file_token_counts: Dict[str, int],
    config: RepomixConfig,
) -> str:
    """Generate token count tree report

    Args:
        processed_files: List of processed files
        file_token_counts: Dictionary of token counts per file
        config: Repomix configuration

    Returns:
        Formatted token count tree string
    """
    # Determine minimum token count threshold
    token_count_tree_config = config.output.token_count_tree
    if isinstance(token_count_tree_config, int):
        min_token_count = token_count_tree_config
    elif isinstance(token_count_tree_config, str) and token_count_tree_config.isdigit():
        min_token_count = int(token_count_tree_config)
    else:
        min_token_count = 0

    # Build files with tokens list
    files_with_tokens: List[FileWithTokens] = []
    for file in processed_files:
        tokens = file_token_counts.get(file.path)
        if tokens is not None:
            files_with_tokens.append(FileWithTokens(path=file.path, tokens=tokens))

    # Build the tree
    tree = build_token_count_tree(files_with_tokens)

    # Format output
    output_lines = ["🔢 Token Count Tree:", "────────────────────"]

    if min_token_count > 0:
        output_lines.append(f"Showing entries with {min_token_count}+ tokens:")

    tree_output = format_token_count_tree(tree, min_token_count)
    output_lines.append(tree_output)

    return "\n".join(output_lines)
