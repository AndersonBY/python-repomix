"""
Test suite for Output Split functionality
"""

import pytest

from src.repomix.core.output.output_split import (
    get_root_entry,
    build_output_split_groups,
    build_split_output_file_path,
    get_utf8_byte_length,
    generate_split_output_parts,
)
from src.repomix.core.output.output_generate import generate_output
from src.repomix.config.config_schema import RepomixConfig
from src.repomix.core.file.file_types import ProcessedFile


class TestGetRootEntry:
    """Test cases for get_root_entry function"""

    def test_get_root_entry_simple_file(self):
        """Test get_root_entry with simple file"""
        assert get_root_entry("file.txt") == "file.txt"

    def test_get_root_entry_nested_path(self):
        """Test get_root_entry with nested path"""
        assert get_root_entry("src/main.py") == "src"

    def test_get_root_entry_deep_nested(self):
        """Test get_root_entry with deeply nested path"""
        assert get_root_entry("src/core/utils/helper.py") == "src"

    def test_get_root_entry_windows_path(self):
        """Test get_root_entry with Windows path separators"""
        assert get_root_entry("src\\main.py") == "src"


class TestBuildOutputSplitGroups:
    """Test cases for build_output_split_groups function"""

    def test_build_groups_single_root(self):
        """Test building groups with single root entry"""
        files = [
            ProcessedFile(path="src/main.py", content="main"),
            ProcessedFile(path="src/utils.py", content="utils"),
        ]
        all_paths = ["src/main.py", "src/utils.py"]

        groups = build_output_split_groups(files, all_paths)

        assert len(groups) == 1
        assert groups[0].root_entry == "src"
        assert len(groups[0].processed_files) == 2

    def test_build_groups_multiple_roots(self):
        """Test building groups with multiple root entries"""
        files = [
            ProcessedFile(path="src/main.py", content="main"),
            ProcessedFile(path="tests/test_main.py", content="test"),
            ProcessedFile(path="docs/readme.md", content="docs"),
        ]
        all_paths = ["src/main.py", "tests/test_main.py", "docs/readme.md"]

        groups = build_output_split_groups(files, all_paths)

        assert len(groups) == 3
        root_entries = [g.root_entry for g in groups]
        assert "src" in root_entries
        assert "tests" in root_entries
        assert "docs" in root_entries

    def test_build_groups_sorted_by_root(self):
        """Test that groups are sorted by root entry"""
        files = [
            ProcessedFile(path="z_folder/file.py", content="z"),
            ProcessedFile(path="a_folder/file.py", content="a"),
            ProcessedFile(path="m_folder/file.py", content="m"),
        ]
        all_paths = [f.path for f in files]

        groups = build_output_split_groups(files, all_paths)

        assert groups[0].root_entry == "a_folder"
        assert groups[1].root_entry == "m_folder"
        assert groups[2].root_entry == "z_folder"


class TestBuildSplitOutputFilePath:
    """Test cases for build_split_output_file_path function"""

    def test_build_path_with_extension(self):
        """Test building split path with extension"""
        result = build_split_output_file_path("output.md", 1)
        assert result == "output.1.md"

    def test_build_path_without_extension(self):
        """Test building split path without extension"""
        result = build_split_output_file_path("output", 2)
        assert result == "output.2"

    def test_build_path_multiple_parts(self):
        """Test building split paths for multiple parts"""
        assert build_split_output_file_path("repomix-output.xml", 1) == "repomix-output.1.xml"
        assert build_split_output_file_path("repomix-output.xml", 2) == "repomix-output.2.xml"
        assert build_split_output_file_path("repomix-output.xml", 10) == "repomix-output.10.xml"


class TestGetUtf8ByteLength:
    """Test cases for get_utf8_byte_length function"""

    def test_ascii_string(self):
        """Test byte length of ASCII string"""
        assert get_utf8_byte_length("hello") == 5

    def test_unicode_string(self):
        """Test byte length of Unicode string"""
        # Chinese characters are 3 bytes each in UTF-8
        assert get_utf8_byte_length("你好") == 6

    def test_empty_string(self):
        """Test byte length of empty string"""
        assert get_utf8_byte_length("") == 0


class TestGenerateSplitOutputParts:
    """Test cases for generate_split_output_parts function"""

    def setup_method(self):
        """Set up test data"""
        self.config = RepomixConfig()
        self.config.output.file_path = "output.md"

    def test_split_invalid_max_bytes(self):
        """Test split with invalid max bytes"""
        with pytest.raises(ValueError, match="Invalid max_bytes_per_part"):
            generate_split_output_parts(
                processed_files=[],
                all_file_paths=[],
                max_bytes_per_part=0,
                base_config=self.config,
                generate_output_fn=generate_output,
                file_char_counts={},
                file_token_counts={},
            )

    def test_split_empty_files(self):
        """Test split with empty files"""
        result = generate_split_output_parts(
            processed_files=[],
            all_file_paths=[],
            max_bytes_per_part=1000,
            base_config=self.config,
            generate_output_fn=generate_output,
            file_char_counts={},
            file_token_counts={},
        )
        assert result == []

    def test_split_single_part(self):
        """Test split that fits in single part"""
        files = [
            ProcessedFile(path="src/main.py", content="print('hello')"),
        ]
        all_paths = ["src/main.py"]
        char_counts = {"src/main.py": 14}
        token_counts = {"src/main.py": 3}

        result = generate_split_output_parts(
            processed_files=files,
            all_file_paths=all_paths,
            max_bytes_per_part=100000,  # Large enough for single part
            base_config=self.config,
            generate_output_fn=generate_output,
            file_char_counts=char_counts,
            file_token_counts=token_counts,
        )

        assert len(result) == 1
        assert result[0].index == 1
        assert "output.1.md" in result[0].file_path

    def test_split_multiple_parts(self):
        """Test split into multiple parts"""
        # Create files that will exceed the limit when combined
        files = [
            ProcessedFile(path="src/main.py", content="x" * 5000),
            ProcessedFile(path="tests/test.py", content="y" * 5000),
        ]
        all_paths = ["src/main.py", "tests/test.py"]
        char_counts = {"src/main.py": 5000, "tests/test.py": 5000}
        token_counts = {"src/main.py": 1000, "tests/test.py": 1000}

        result = generate_split_output_parts(
            processed_files=files,
            all_file_paths=all_paths,
            max_bytes_per_part=8000,  # Small enough to force split but large enough for single group
            base_config=self.config,
            generate_output_fn=generate_output,
            file_char_counts=char_counts,
            file_token_counts=token_counts,
        )

        # Should create multiple parts
        assert len(result) >= 1
        for i, part in enumerate(result):
            assert part.index == i + 1


if __name__ == "__main__":
    pytest.main([__file__])
