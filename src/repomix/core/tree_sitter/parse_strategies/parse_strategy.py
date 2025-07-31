"""Base parse strategy interface and factory."""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Type
from tree_sitter import Node

logger = logging.getLogger(__name__)


class ParsedChunk:
    """Represents a parsed chunk of code."""
    
    def __init__(self, content: str, start_line: int, end_line: int, node_type: str):
        self.content = content.strip()
        self.start_line = start_line
        self.end_line = end_line
        self.node_type = node_type
        self.normalized_content = self._normalize_content(self.content)
    
    def _normalize_content(self, content: str) -> str:
        """Normalize content for deduplication purposes."""
        # Remove extra whitespace and normalize line endings
        lines = [line.strip() for line in content.split('\n')]
        return '\n'.join(line for line in lines if line)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ParsedChunk):
            return NotImplemented
        return self.normalized_content == other.normalized_content
    
    def __hash__(self) -> int:
        return hash(self.normalized_content)
    
    def can_merge_with(self, other: 'ParsedChunk') -> bool:
        """Check if this chunk can be merged with another (adjacent lines)."""
        return abs(self.end_line - other.start_line) <= 1 or abs(other.end_line - self.start_line) <= 1


class ParseStrategy(ABC):
    """Abstract base class for language-specific parse strategies."""
    
    @abstractmethod
    def process_captures(self, captures: List[tuple], source_lines: List[str]) -> List[ParsedChunk]:
        """Process tree-sitter query captures into parsed chunks.
        
        Args:
            captures: List of (node, capture_name) tuples from tree-sitter query
            source_lines: List of source code lines
            
        Returns:
            List of parsed chunks
        """
        pass
    
    def deduplicate_chunks(self, chunks: List[ParsedChunk]) -> List[ParsedChunk]:
        """Remove duplicate chunks based on normalized content."""
        seen = set()
        unique_chunks = []
        
        for chunk in chunks:
            if chunk not in seen:
                seen.add(chunk)
                unique_chunks.append(chunk)
        
        return unique_chunks
    
    def merge_adjacent_chunks(self, chunks: List[ParsedChunk]) -> List[ParsedChunk]:
        """Merge adjacent chunks that are on consecutive lines."""
        if not chunks:
            return chunks
        
        # Sort chunks by start line
        sorted_chunks = sorted(chunks, key=lambda c: c.start_line)
        merged = [sorted_chunks[0]]
        
        for current in sorted_chunks[1:]:
            last_merged = merged[-1]
            
            # Only merge chunks that are truly adjacent (no gaps) and of same type
            # This preserves separate chunks for proper separator usage
            if (last_merged.end_line + 1 >= current.start_line and 
                last_merged.node_type == current.node_type):
                # Merge the chunks without adding extra separators
                new_content = last_merged.content + '\n' + current.content
                new_chunk = ParsedChunk(
                    content=new_content,
                    start_line=min(last_merged.start_line, current.start_line),
                    end_line=max(last_merged.end_line, current.end_line),
                    node_type=last_merged.node_type
                )
                merged[-1] = new_chunk
            else:
                merged.append(current)
        
        return merged
    
    def extract_node_content(self, node: Node, source_lines: List[str]) -> str:
        """Extract the text content of a node from source lines."""
        start_line = node.start_point[0]
        end_line = node.end_point[0]
        start_col = node.start_point[1]
        end_col = node.end_point[1]
        
        if start_line == end_line:
            # Single line node
            if start_line < len(source_lines):
                line = source_lines[start_line]
                return line[start_col:end_col]
        else:
            # Multi-line node
            lines = []
            for i in range(start_line, min(end_line + 1, len(source_lines))):
                line = source_lines[i]
                if i == start_line:
                    lines.append(line[start_col:])
                elif i == end_line:
                    lines.append(line[:end_col])
                else:
                    lines.append(line)
            return '\n'.join(lines)
        
        return ""


class ParseStrategyFactory:
    """Factory for creating language-specific parse strategies."""
    
    _strategies: Dict[str, Type[ParseStrategy]] = {}
    
    @classmethod
    def register_strategy(cls, language: str, strategy_class: Type[ParseStrategy]) -> None:
        """Register a parse strategy for a language."""
        cls._strategies[language] = strategy_class
    
    @classmethod
    def create_strategy(cls, language: str) -> ParseStrategy:
        """Create a parse strategy for the given language."""
        if language in cls._strategies:
            return cls._strategies[language]()
        
        # Fall back to default strategy
        from .default_parse_strategy import DefaultParseStrategy
        logger.debug(f"Using default parse strategy for language: {language}")
        return DefaultParseStrategy()