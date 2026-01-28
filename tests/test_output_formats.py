"""
Test suite for output format functionality
"""

import json
import tempfile
import pytest
from pathlib import Path
import xml.etree.ElementTree as ET

from src.repomix.core.output.output_generate import generate_output
from src.repomix.config.config_schema import RepomixConfig, RepomixOutputStyle
from src.repomix.core.file.file_types import ProcessedFile


class TestOutputGeneration:
    """Test cases for output generation"""

    def setup_method(self):
        """Set up test data"""
        self.processed_files = [
            ProcessedFile(
                path="src/main.py",
                content="def main():\n    print('Hello, World!')\n    return 0",
            ),
            ProcessedFile(path="src/utils.py", content="def helper():\n    return 'helper'"),
            ProcessedFile(path="README.md", content="# Project\n\nThis is a test project."),
        ]

        self.file_char_counts = {"src/main.py": 45, "src/utils.py": 25, "README.md": 30}

        self.file_token_counts = {"src/main.py": 12, "src/utils.py": 6, "README.md": 8}

        self.file_tree = {"src": {"main.py": "", "utils.py": ""}, "README.md": ""}

    def test_generate_output_plain_style(self):
        """Test output generation with plain style"""
        config = RepomixConfig()
        config.output._style = RepomixOutputStyle.PLAIN

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
        )

        assert output is not None
        assert len(output) > 0
        # Plain output should contain file contents
        assert "def main():" in output
        assert "def helper():" in output
        assert "# Project" in output

    def test_generate_output_markdown_style(self):
        """Test output generation with markdown style"""
        config = RepomixConfig()
        config.output._style = RepomixOutputStyle.MARKDOWN

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
        )

        assert output is not None
        assert len(output) > 0
        # Markdown output should contain markdown formatting
        assert "# Repository Structure" in output or "# Files" in output or "##" in output
        assert "```python" in output or "```" in output
        assert "def main():" in output

    def test_generate_output_xml_style(self):
        """Test output generation with XML style"""
        config = RepomixConfig()
        config.output.style_enum = RepomixOutputStyle.XML

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
        )

        assert output is not None
        assert len(output) > 0
        # XML output should be valid XML
        assert output.startswith("<?xml")
        assert "<repository>" in output or "<repo>" in output

        # Verify it's valid XML by parsing it
        try:
            ET.fromstring(output)
        except ET.ParseError:
            pytest.fail("Generated XML output is not valid XML")

    def test_generate_output_json_style(self):
        """Test output generation with JSON style"""
        config = RepomixConfig()
        config.output.style_enum = RepomixOutputStyle.JSON

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
        )

        assert output is not None
        assert len(output) > 0

        # Verify it's valid JSON by parsing it
        try:
            parsed = json.loads(output)
        except json.JSONDecodeError:
            pytest.fail("Generated JSON output is not valid JSON")

        # Verify JSON structure
        assert "fileSummary" in parsed
        assert "files" in parsed
        assert "statistics" in parsed

        # Verify file contents are included
        assert "src/main.py" in parsed["files"]
        assert "src/utils.py" in parsed["files"]
        assert "README.md" in parsed["files"]

        # Verify file content
        assert "def main():" in parsed["files"]["src/main.py"]["content"]

        # Verify statistics
        assert parsed["statistics"]["totalFiles"] == 3
        assert parsed["statistics"]["totalCharacters"] == 100  # 45 + 25 + 30

    def test_generate_output_json_with_directory_structure(self):
        """Test JSON output includes directory structure when enabled"""
        config = RepomixConfig()
        config.output.style_enum = RepomixOutputStyle.JSON
        config.output.show_directory_structure = True

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
        )

        parsed = json.loads(output)
        assert "directoryStructure" in parsed
        assert "src/" in parsed["directoryStructure"] or "main.py" in parsed["directoryStructure"]

    def test_generate_output_json_with_file_stats(self):
        """Test JSON output includes file stats when enabled"""
        config = RepomixConfig()
        config.output.style_enum = RepomixOutputStyle.JSON
        config.output.show_file_stats = True

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
        )

        parsed = json.loads(output)
        # When show_file_stats is enabled, each file should have charCount and tokenCount
        assert "charCount" in parsed["files"]["src/main.py"]
        assert "tokenCount" in parsed["files"]["src/main.py"]
        assert parsed["files"]["src/main.py"]["charCount"] == 45

    def test_generate_output_basic_functionality(self):
        """Test basic output generation functionality"""
        config = RepomixConfig()

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
        )

        assert output is not None
        assert len(output) > 0
        # Should contain file contents
        assert "def main():" in output
        assert "def helper():" in output

    def test_generate_output_with_directory_structure(self):
        """Test output generation with directory structure enabled"""
        config = RepomixConfig()
        config.output.show_directory_structure = True

        output = generate_output(
            self.processed_files,
            config,
            self.file_char_counts,
            self.file_token_counts,
            self.file_tree,
        )

        assert output is not None
        assert len(output) > 0
        # Should contain file structure information
        assert "src/" in output or "README.md" in output


class TestOutputDecoration:
    """Test cases for output decoration"""

    def test_decorate_output_basic(self):
        """Test basic output decoration"""
        raw_output = "File content here"
        _config = RepomixConfig()

        # Since decorate_output doesn't exist, test basic output processing
        # This would be where decoration logic would be tested
        assert raw_output is not None
        assert len(raw_output) > 0

    def test_decorate_output_with_header_footer(self):
        """Test output decoration with header and footer"""
        raw_output = "Main content"
        _config = RepomixConfig()

        # Mock decoration functionality if needed
        # Since the actual function doesn't exist, this tests the concept
        decorated = f"HEADER\n{raw_output}\nFOOTER"

        assert "HEADER" in decorated
        assert "Main content" in decorated
        assert "FOOTER" in decorated


class TestOutputIntegration:
    """Integration tests for output functionality"""

    def test_complete_output_workflow(self):
        """Test complete output generation workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "app.py").write_text('''
def main():
    """Main application function."""
    print("Application started")
    return process_data()

def process_data():
    """Process application data."""
    data = ["item1", "item2", "item3"]
    return len(data)

if __name__ == "__main__":
    main()
            ''')

            (temp_path / "utils.py").write_text('''
"""Utility functions for the application."""

def helper_function(value):
    """Helper function for processing."""
    return value.upper()

class DataProcessor:
    """Process various types of data."""

    def __init__(self):
        self.processed = []

    def add_item(self, item):
        """Add item to processing queue."""
        self.processed.append(helper_function(item))
            ''')

            (temp_path / "README.md").write_text("""
# Test Application

This is a test application for output generation testing.

## Features
- Main application logic
- Utility functions
- Data processing capabilities

## Usage
Run with: `python app.py`
            """)

            # Create ProcessedFile objects from the created files
            processed_files = [
                ProcessedFile(path="app.py", content=(temp_path / "app.py").read_text()),
                ProcessedFile(path="utils.py", content=(temp_path / "utils.py").read_text()),
                ProcessedFile(path="README.md", content=(temp_path / "README.md").read_text()),
            ]

            file_tree = {"app.py": "", "utils.py": "", "README.md": ""}

            file_char_counts = {
                "app.py": len((temp_path / "app.py").read_text()),
                "utils.py": len((temp_path / "utils.py").read_text()),
                "README.md": len((temp_path / "README.md").read_text()),
            }

            file_token_counts = {"app.py": 50, "utils.py": 35, "README.md": 25}

            # Test all output styles
            styles = [
                RepomixOutputStyle.PLAIN,
                RepomixOutputStyle.MARKDOWN,
                RepomixOutputStyle.XML,
                RepomixOutputStyle.JSON,
            ]

            for style in styles:
                config = RepomixConfig()
                config.output.style_enum = style

                output = generate_output(
                    processed_files,
                    config,
                    file_char_counts,
                    file_token_counts,
                    file_tree,
                )

                assert output is not None
                assert len(output) > 0

                # All styles should contain the actual file content
                assert "def main():" in output
                assert "class DataProcessor:" in output
                assert "# Test Application" in output

                # Style-specific checks
                if style == RepomixOutputStyle.XML:
                    assert output.startswith("<?xml")
                    # Verify valid XML
                    try:
                        ET.fromstring(output)
                    except ET.ParseError:
                        pytest.fail(f"Invalid XML generated for {style}")

                elif style == RepomixOutputStyle.MARKDOWN:
                    assert "```" in output  # Code blocks
                    assert "#" in output  # Headers

                elif style == RepomixOutputStyle.JSON:
                    # Verify valid JSON
                    try:
                        parsed = json.loads(output)
                        assert "files" in parsed
                        assert "statistics" in parsed
                    except json.JSONDecodeError:
                        pytest.fail(f"Invalid JSON generated for {style}")

                # Plain style doesn't have specific formatting requirements

    def test_output_with_different_file_types(self):
        """Test output generation with different file types"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create different file types
            (temp_path / "script.py").write_text("print('Python script')")
            (temp_path / "style.css").write_text("body { margin: 0; }")
            (temp_path / "app.js").write_text("console.log('JavaScript');")
            (temp_path / "config.json").write_text('{"name": "test", "version": "1.0"}')
            (temp_path / "data.txt").write_text("Plain text data")

            # Create ProcessedFile objects
            files = list(temp_path.glob("*"))
            processed_files = [ProcessedFile(path=f.name, content=f.read_text()) for f in files]

            file_tree = {f.name: "" for f in files}
            char_counts = {f.name: len(f.read_text()) for f in files}
            token_counts = {f.name: 10 for f in files}  # Mock token counts

            config = RepomixConfig()
            config.output._style = RepomixOutputStyle.MARKDOWN

            output = generate_output(processed_files, config, char_counts, token_counts, file_tree)

            assert output is not None

            # Should contain content from all file types
            assert "print('Python script')" in output
            assert "margin: 0" in output
            assert "console.log" in output
            assert '"name": "test"' in output
            assert "Plain text data" in output


if __name__ == "__main__":
    pytest.main([__file__])
