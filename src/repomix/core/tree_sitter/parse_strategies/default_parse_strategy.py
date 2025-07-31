"""Default parse strategy for unsupported languages."""

import logging
from typing import List

from .parse_strategy import ParseStrategy, ParsedChunk

logger = logging.getLogger(__name__)


class DefaultParseStrategy(ParseStrategy):
    """Default parse strategy that extracts basic elements like comments and names."""
    
    def process_captures(self, captures: List[tuple], source_lines: List[str]) -> List[ParsedChunk]:
        """Process captures using a generic approach."""
        chunks = []
        
        for node, capture_name in captures:
            try:
                content = self.extract_node_content(node, source_lines)
                
                if not content.strip():
                    continue
                
                # Create chunk based on capture type
                chunk = ParsedChunk(
                    content=content,
                    start_line=node.start_point[0],
                    end_line=node.end_point[0],
                    node_type=capture_name
                )
                
                chunks.append(chunk)
                
            except Exception as e:
                logger.warning(f"Error processing capture {capture_name}: {e}")
                continue
        
        # Deduplicate and merge
        chunks = self.deduplicate_chunks(chunks)
        chunks = self.merge_adjacent_chunks(chunks)
        
        return chunks