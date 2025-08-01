"""Go-specific parse strategy."""

import logging
from typing import List
from tree_sitter import Node

from .parse_strategy import ParseStrategy, ParsedChunk, ParseStrategyFactory

logger = logging.getLogger(__name__)


class GoParseStrategy(ParseStrategy):
    """Parse strategy specifically designed for Go code."""

    def process_captures(self, captures: List[tuple], source_lines: List[str]) -> List[ParsedChunk]:
        """Process Go-specific captures."""
        chunks = []

        for node, capture_name in captures:
            try:
                content = self._process_go_capture(node, capture_name, source_lines)

                if not content.strip():
                    continue

                chunk = ParsedChunk(
                    content=content,
                    start_line=node.start_point[0],
                    end_line=node.end_point[0],
                    node_type=capture_name,
                )

                chunks.append(chunk)

            except Exception as e:
                logger.warning(f"Error processing Go capture {capture_name}: {e}")
                continue

        # Deduplicate and merge
        chunks = self.deduplicate_chunks(chunks)
        chunks = self.merge_adjacent_chunks(chunks)

        return chunks

    def _process_go_capture(self, node: Node, capture_name: str, source_lines: List[str]) -> str:
        """Process a specific Go capture based on its type."""
        if capture_name == "comment":
            return self._process_comment(node, source_lines)
        elif capture_name == "definition.package":
            return self._process_package_declaration(node, source_lines)
        elif capture_name == "definition.import":
            return self._process_import(node, source_lines)
        elif capture_name == "definition.function":
            return self._process_function_definition(node, source_lines)
        elif capture_name == "definition.method":
            return self._process_method_definition(node, source_lines)
        elif capture_name == "definition.type":
            return self._process_type_definition(node, source_lines)
        elif capture_name == "definition.interface":
            return self._process_interface_definition(node, source_lines)
        elif capture_name == "definition.struct":
            return self._process_struct_definition(node, source_lines)
        elif capture_name == "definition.var":
            return self._process_var_declaration(node, source_lines)
        elif capture_name == "definition.const":
            return self._process_const_declaration(node, source_lines)
        else:
            return self.extract_node_content(node, source_lines)

    def _process_comment(self, node: Node, source_lines: List[str]) -> str:
        """Process Go comments."""
        return self.extract_node_content(node, source_lines)

    def _process_package_declaration(self, node: Node, source_lines: List[str]) -> str:
        """Process Go package declarations."""
        return self.extract_node_content(node, source_lines)

    def _process_import(self, node: Node, source_lines: List[str]) -> str:
        """Process Go import statements."""
        return self.extract_node_content(node, source_lines)

    def _process_function_definition(self, node: Node, source_lines: List[str]) -> str:
        """Process Go function definitions, extracting signature only."""
        content_lines = []

        # Extract function signature (everything before the opening brace)
        for i in range(node.start_point[0], min(node.end_point[0] + 1, len(source_lines))):
            line = source_lines[i]
            content_lines.append(line)

            # Stop at opening brace for function body
            if "{" in line:
                brace_index = line.find("{")
                truncated_line = line[: brace_index + 1]
                content_lines[-1] = truncated_line
                break

        return "\n".join(content_lines)

    def _process_method_definition(self, node: Node, source_lines: List[str]) -> str:
        """Process Go method definitions (functions with receivers)."""
        return self._process_function_definition(node, source_lines)

    def _process_type_definition(self, node: Node, source_lines: List[str]) -> str:
        """Process Go type definitions."""
        return self.extract_node_content(node, source_lines)

    def _process_interface_definition(self, node: Node, source_lines: List[str]) -> str:
        """Process Go interface definitions."""
        return self.extract_node_content(node, source_lines)

    def _process_struct_definition(self, node: Node, source_lines: List[str]) -> str:
        """Process Go struct definitions."""
        return self.extract_node_content(node, source_lines)

    def _process_var_declaration(self, node: Node, source_lines: List[str]) -> str:
        """Process Go variable declarations."""
        return self.extract_node_content(node, source_lines)

    def _process_const_declaration(self, node: Node, source_lines: List[str]) -> str:
        """Process Go constant declarations."""
        return self.extract_node_content(node, source_lines)


# Register the Go strategy
ParseStrategyFactory.register_strategy("go", GoParseStrategy)
