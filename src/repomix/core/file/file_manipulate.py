"""
File Manipulation Module - Provides Various Methods for File Content Operations
"""

import re
import ast
import warnings
from typing import Dict
from pathlib import Path

from ..tree_sitter.parse_file import parse_file, can_parse_file


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

    def compress_code(self, content: str, keep_signatures: bool = True, keep_docstrings: bool = False, keep_interfaces: bool = False) -> str:
        """Compress code by removing unnecessary elements

        Args:
            content: File content
            keep_signatures: Whether to keep function/class signatures
            keep_docstrings: Whether to keep docstrings
            keep_interfaces: Whether to keep only interface (signatures + docstrings, but remove implementation)

        Returns:
            Compressed content
        """
        warnings.warn("Code compression not implemented for this file type", UserWarning)
        return content


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

    def compress_code(self, content: str, keep_signatures: bool = True, keep_docstrings: bool = False, keep_interfaces: bool = False) -> str:
        """Compress Python code using AST

        Args:
            content: Python source code
            keep_signatures: Whether to keep function/class signatures
            keep_docstrings: Whether to keep docstrings
            keep_interfaces: Whether to keep only interface (signatures + docstrings, but remove implementation)

        Returns:
            Compressed Python code
        """
        try:
            tree = ast.parse(content)
            compressed_tree = self._compress_ast_node(tree, keep_signatures, keep_docstrings, keep_interfaces)
            if compressed_tree is not None:
                return ast.unparse(compressed_tree)
            else:
                return ""
        except SyntaxError:
            warnings.warn("Failed to parse Python code for compression, returning original content", UserWarning)
            return content
        except Exception as e:
            warnings.warn(f"Error during Python code compression: {e}, returning original content", UserWarning)
            return content

    def _compress_ast_node(self, node: ast.AST, keep_signatures: bool, keep_docstrings: bool, keep_interfaces: bool) -> ast.AST | None:
        """Recursively compress AST nodes

        Args:
            node: AST node to compress
            keep_signatures: Whether to keep function/class signatures
            keep_docstrings: Whether to keep docstrings
            keep_interfaces: Whether to keep only interface (signatures + docstrings, but remove implementation)

        Returns:
            Compressed AST node, or None if node should be removed
        """
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return self._compress_function_or_class(node, keep_signatures, keep_docstrings, keep_interfaces)
        elif isinstance(node, ast.Module):
            # Process module body
            new_body = []
            for child in node.body:
                compressed_child = self._compress_ast_node(child, keep_signatures, keep_docstrings, keep_interfaces)
                if compressed_child is not None:
                    new_body.append(compressed_child)
            node.body = new_body
            return node
        else:
            # For other nodes, recursively process children
            for field, value in ast.iter_fields(node):
                if isinstance(value, list):
                    new_list = []
                    for item in value:
                        if isinstance(item, ast.AST):
                            compressed_item = self._compress_ast_node(item, keep_signatures, keep_docstrings, keep_interfaces)
                            if compressed_item is not None:
                                new_list.append(compressed_item)
                        else:
                            new_list.append(item)
                    setattr(node, field, new_list)
                elif isinstance(value, ast.AST):
                    compressed_value = self._compress_ast_node(value, keep_signatures, keep_docstrings, keep_interfaces)
                    if compressed_value is not None:
                        setattr(node, field, compressed_value)
            return node

    def _compress_function_or_class(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef, keep_signatures: bool, keep_docstrings: bool, keep_interfaces: bool
    ) -> ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | None:
        """Compress function or class definition

        Args:
            node: Function or class AST node
            keep_signatures: Whether to keep function/class signatures
            keep_docstrings: Whether to keep docstrings
            keep_interfaces: Whether to keep only interface (signatures + docstrings, but remove implementation)

        Returns:
            Compressed function or class node, or None if completely removed
        """
        if not keep_signatures:
            # If not keeping signatures, remove the entire function/class
            return None

        # Handle interface mode
        if keep_interfaces:
            new_body = []

            # Handle docstring - always keep in interface mode
            first_stmt = node.body[0] if node.body else None
            if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant) and isinstance(first_stmt.value.value, str):
                # This is a docstring - keep it
                new_body.append(first_stmt)
                body_to_process = node.body[1:]
            else:
                body_to_process = node.body

            # For classes in interface mode, recursively process methods to keep their interfaces
            if isinstance(node, ast.ClassDef):
                for stmt in body_to_process:
                    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Recursively process methods to keep their interfaces
                        compressed_method = self._compress_ast_node(stmt, keep_signatures, keep_docstrings, keep_interfaces)
                        if compressed_method is not None:
                            new_body.append(compressed_method)
                    # Skip other statements in class body (like assignments, etc.)

            # If no methods were added (for functions or empty classes), add pass
            if len(new_body) <= 1:  # Only docstring or nothing
                new_body.append(ast.Pass())

            node.body = new_body
            return node

        # Keep the signature but compress the body
        if hasattr(node, "body") and node.body:
            new_body = []

            # Handle docstring
            first_stmt = node.body[0] if node.body else None
            if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant) and isinstance(first_stmt.value.value, str):
                # This is a docstring
                if keep_docstrings:
                    new_body.append(first_stmt)
                # Skip the docstring in further processing
                body_to_process = node.body[1:]
            else:
                body_to_process = node.body

            # Process the rest of the body
            for stmt in body_to_process:
                compressed_stmt = self._compress_ast_node(stmt, keep_signatures, keep_docstrings, keep_interfaces)
                if compressed_stmt is not None:
                    new_body.append(compressed_stmt)

            # If body is empty after compression, add a pass statement
            if not new_body:
                new_body.append(ast.Pass())

            node.body = new_body

        return node


class TreeSitterManipulator(FileManipulator):
    """Tree-sitter based file manipulator for code compression"""
    
    def __init__(self, file_path: str):
        """Initialize with file path for language detection
        
        Args:
            file_path: Path to the file being processed
        """
        super().__init__()
        self.file_path = file_path
    
    def compress_code(self, content: str, keep_signatures: bool = True, keep_docstrings: bool = False, keep_interfaces: bool = False) -> str:
        """Compress code using tree-sitter parsing
        
        Args:
            content: File content
            keep_signatures: Whether to keep function/class signatures (unused, always True for tree-sitter)
            keep_docstrings: Whether to keep docstrings (unused, tree-sitter handles this)
            keep_interfaces: Whether to keep only interface (unused, tree-sitter handles this)
            
        Returns:
            Compressed content using tree-sitter, or fallback compression if parsing fails
        """
        if not can_parse_file(self.file_path):
            return self._fallback_compression(content, keep_signatures, keep_docstrings, keep_interfaces)
        
        try:
            compressed = parse_file(content, self.file_path)
            if compressed is not None:
                # Tree-sitter parsing succeeded, use it regardless of size
                # Tree-sitter provides structural compression with separators
                return compressed
            else:
                # Tree-sitter parsing failed, use fallback
                return self._fallback_compression(content, keep_signatures, keep_docstrings, keep_interfaces)
        except Exception as e:
            warnings.warn(f"Tree-sitter compression failed for {self.file_path}: {e}", UserWarning)
            return self._fallback_compression(content, keep_signatures, keep_docstrings, keep_interfaces)
    
    def _fallback_compression(self, content: str, keep_signatures: bool = True, keep_docstrings: bool = False, keep_interfaces: bool = False) -> str:
        """Fallback to traditional compression based on file extension
        
        Args:
            content: File content
            keep_signatures: Whether to keep function/class signatures
            keep_docstrings: Whether to keep docstrings  
            keep_interfaces: Whether to keep only interface
            
        Returns:
            Compressed content using traditional methods
        """
        from pathlib import Path
        ext = Path(self.file_path).suffix
        
        # Try traditional manipulator for this file extension
        traditional_manipulator = manipulators.get(ext)
        if traditional_manipulator:
            try:
                return traditional_manipulator.compress_code(content, keep_signatures, keep_docstrings, keep_interfaces)
            except Exception as e:
                warnings.warn(f"Fallback compression failed for {self.file_path}: {e}", UserWarning)
        
        # Final fallback: return original content
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

    def compress_code(self, content: str, keep_signatures: bool = True, keep_docstrings: bool = False, keep_interfaces: bool = False) -> str:
        """Compress code using all manipulators"""
        for manipulator in self.manipulators:
            content = manipulator.compress_code(content, keep_signatures, keep_docstrings, keep_interfaces)
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
    file_path_str = str(file_path)
    
    # First try tree-sitter manipulator if file can be parsed
    if can_parse_file(file_path_str):
        return TreeSitterManipulator(file_path_str)
    
    # Fallback to traditional manipulators
    ext = Path(file_path).suffix
    return manipulators.get(ext)
