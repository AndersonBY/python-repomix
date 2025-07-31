"""Python-specific parse strategy."""

import logging
from typing import List
from tree_sitter import Node

from .parse_strategy import ParseStrategy, ParsedChunk, ParseStrategyFactory

logger = logging.getLogger(__name__)


class PythonParseStrategy(ParseStrategy):
    """Parse strategy specifically designed for Python code."""
    
    def process_captures(self, captures: List[tuple], source_lines: List[str]) -> List[ParsedChunk]:
        """Process Python-specific captures."""
        chunks = []
        
        for node, capture_name in captures:
            try:
                content = self._process_python_capture(node, capture_name, source_lines)
                
                if not content.strip():
                    continue
                
                chunk = ParsedChunk(
                    content=content,
                    start_line=node.start_point[0],
                    end_line=node.end_point[0],
                    node_type=capture_name
                )
                
                chunks.append(chunk)
                
            except Exception as e:
                logger.warning(f"Error processing Python capture {capture_name}: {e}")
                continue
        
        # Deduplicate and merge
        chunks = self.deduplicate_chunks(chunks)
        chunks = self.merge_adjacent_imports(chunks)
        chunks = self.merge_adjacent_chunks(chunks)
        
        return chunks
    
    def _process_python_capture(self, node: Node, capture_name: str, source_lines: List[str]) -> str:
        """Process a specific Python capture based on its type."""
        if capture_name == "definition.class":
            return self._process_class_definition(node, source_lines)
        elif capture_name == "definition.function":
            return self._process_function_definition(node, source_lines)
        elif capture_name == "definition.import":
            return self._process_import(node, source_lines)
        elif capture_name == "definition.variable":
            return self._process_variable_assignment(node, source_lines)
        elif capture_name == "definition.decorator":
            return self._process_decorator(node, source_lines)
        elif capture_name.startswith("statement."):
            return self._process_statement(node, source_lines)
        else:
            # Default: extract the full node content
            return self.extract_node_content(node, source_lines)
    
    def _process_comment(self, node: Node, source_lines: List[str]) -> str:
        """Process Python comments."""
        return self.extract_node_content(node, source_lines)
    
    def _process_class_definition(self, node: Node, source_lines: List[str]) -> str:
        """Process Python class definitions, including decorators and docstrings."""
        # Find decorators that precede this class
        content_lines = []
        
        # Get the class definition line
        class_line = node.start_point[0]
        
        # Look for decorators before the class
        for i in range(max(0, class_line - 5), class_line):
            line = source_lines[i].strip()
            if line.startswith('@'):
                content_lines.append(source_lines[i])
        
        # Add the class definition line(s)
        for i in range(node.start_point[0], min(node.end_point[0] + 1, len(source_lines))):
            line = source_lines[i]
            content_lines.append(line)
            # Stop after class definition (before any methods/content)
            if line.strip().endswith(':'):
                break
        
        # Look for docstring
        if node.children:
            for child in node.children:
                if child.type == 'block':
                    # Check first statement in block for docstring
                    for stmt in child.children:
                        if stmt.type == 'expression_statement':
                            for expr_child in stmt.children:
                                if expr_child.type == 'string':
                                    docstring = self.extract_node_content(expr_child, source_lines)
                                    content_lines.append(f"    {docstring}")
                                    break
                    break
        
        return '\n'.join(content_lines)
    
    def _process_function_definition(self, node: Node, source_lines: List[str]) -> str:
        """Process Python function definitions, including decorators and signatures."""
        content_lines = []
        
        # Get the function definition line
        func_line = node.start_point[0]
        
        # Look for decorators before the function
        for i in range(max(0, func_line - 5), func_line):
            line = source_lines[i].strip()
            if line.startswith('@'):
                content_lines.append(source_lines[i])
        
        # Add the function signature (everything until the colon)
        in_signature = True
        for i in range(node.start_point[0], min(node.end_point[0] + 1, len(source_lines))):
            line = source_lines[i]
            content_lines.append(line)
            if in_signature and line.strip().endswith(':'):
                in_signature = False
                break
        
        # Look for docstring
        if node.children:
            for child in node.children:
                if child.type == 'block':
                    # Check first statement in block for docstring
                    for stmt in child.children:
                        if stmt.type == 'expression_statement':
                            for expr_child in stmt.children:
                                if expr_child.type == 'string':
                                    docstring = self.extract_node_content(expr_child, source_lines)
                                    content_lines.append(f"    {docstring}")
                                    break
                    break
        
        return '\n'.join(content_lines)
    
    def _process_import(self, node: Node, source_lines: List[str]) -> str:
        """Process Python import statements."""
        return self.extract_node_content(node, source_lines)
    
    def _process_variable_assignment(self, node: Node, source_lines: List[str]) -> str:
        """Process Python variable assignments."""
        return self.extract_node_content(node, source_lines)
    
    def _process_decorator(self, node: Node, source_lines: List[str]) -> str:
        """Process Python decorators."""
        return self.extract_node_content(node, source_lines)
    
    def _process_statement(self, node: Node, source_lines: List[str]) -> str:
        """Process Python statements (global, nonlocal, etc.)."""
        return self.extract_node_content(node, source_lines)
    
    def merge_adjacent_imports(self, chunks: List[ParsedChunk]) -> List[ParsedChunk]:
        """Merge adjacent import statements that are separated by at most one blank line."""
        if not chunks:
            return chunks
        
        # Sort chunks by start line
        sorted_chunks = sorted(chunks, key=lambda c: c.start_line)
        merged = []
        
        i = 0
        while i < len(sorted_chunks):
            current = sorted_chunks[i]
            
            # Only process import chunks
            if current.node_type == "definition.import":
                # Collect all adjacent imports (allowing one blank line between them)
                import_group = [current]
                j = i + 1
                
                while j < len(sorted_chunks):
                    next_chunk = sorted_chunks[j]
                    if (next_chunk.node_type == "definition.import" and 
                        next_chunk.start_line - import_group[-1].end_line <= 2):
                        import_group.append(next_chunk)
                        j += 1
                    else:
                        break
                
                # If we have multiple imports, merge them
                if len(import_group) > 1:
                    # Combine the content of all imports in the group
                    combined_lines = []
                    for imp in import_group:
                        combined_lines.append(imp.content)
                    
                    new_chunk = ParsedChunk(
                        content='\n'.join(combined_lines),
                        start_line=import_group[0].start_line,
                        end_line=import_group[-1].end_line,
                        node_type="definition.import"
                    )
                    merged.append(new_chunk)
                    i = j
                else:
                    merged.append(current)
                    i += 1
            else:
                merged.append(current)
                i += 1
        
        return merged


# Register the Python strategy
ParseStrategyFactory.register_strategy('python', PythonParseStrategy)