"""
Test suite for Full Directory Structure functionality
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.repomix.core.repo_processor import (
    build_full_file_tree,
    build_file_tree_with_ignore,
)
from src.repomix.core.output.output_generate import (
    build_filtered_file_tree,
    generate_output,
)
from src.repomix.core.file.file_types import ProcessedFile
from src.repomix.config.config_schema import RepomixConfig


class TestBuildFullFileTree:
    """Test cases for build_full_file_tree function"""

    def test_basic_structure(self, tmp_path):
        """Test basic directory structure"""
        # Create test structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_main.py").write_text("def test(): pass")
        (tmp_path / "README.md").write_text("# README")

        result = build_full_file_tree(tmp_path)

        assert "src" in result
        assert "main.py" in result["src"]
        assert "tests" in result
        assert "test_main.py" in result["tests"]
        assert "README.md" in result

    def test_includes_hidden_files(self, tmp_path):
        """Test that hidden files are included"""
        (tmp_path / ".gitignore").write_text("*.pyc")
        (tmp_path / ".env").write_text("SECRET=123")
        (tmp_path / "main.py").write_text("print('hello')")

        result = build_full_file_tree(tmp_path)

        assert ".gitignore" in result
        assert ".env" in result
        assert "main.py" in result

    def test_includes_ignored_directories(self, tmp_path):
        """Test that normally ignored directories are included"""
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "package.json").write_text("{}")
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "main.cpython-39.pyc").write_text("")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')")

        result = build_full_file_tree(tmp_path)

        assert "node_modules" in result
        assert "package.json" in result["node_modules"]
        assert "__pycache__" in result
        assert "src" in result

    def test_empty_directories(self, tmp_path):
        """Test that empty directories are included"""
        (tmp_path / "empty_dir").mkdir()
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')")

        result = build_full_file_tree(tmp_path)

        assert "empty_dir" in result
        assert result["empty_dir"] == {}
        assert "src" in result

    def test_nested_structure(self, tmp_path):
        """Test deeply nested directory structure"""
        nested = tmp_path / "a" / "b" / "c" / "d"
        nested.mkdir(parents=True)
        (nested / "deep.py").write_text("# deep")

        result = build_full_file_tree(tmp_path)

        assert "a" in result
        assert "b" in result["a"]
        assert "c" in result["a"]["b"]
        assert "d" in result["a"]["b"]["c"]
        assert "deep.py" in result["a"]["b"]["c"]["d"]


class TestBuildFileTreeWithIgnore:
    """Test cases for build_file_tree_with_ignore function"""

    def test_ignores_node_modules(self, tmp_path):
        """Test that node_modules is ignored by default"""
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "package.json").write_text("{}")
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')")

        config = RepomixConfig()
        result = build_file_tree_with_ignore(tmp_path, config)

        assert "node_modules" not in result
        assert "src" in result

    def test_ignores_pycache(self, tmp_path):
        """Test that __pycache__ is ignored by default"""
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "main.cpython-39.pyc").write_text("")
        (tmp_path / "main.py").write_text("print('hello')")

        config = RepomixConfig()
        result = build_file_tree_with_ignore(tmp_path, config)

        assert "__pycache__" not in result
        assert "main.py" in result


class TestBuildFilteredFileTree:
    """Test cases for build_filtered_file_tree function"""

    def test_only_includes_processed_files(self):
        """Test that only processed files are included"""
        files = [
            ProcessedFile(path="src/main.py", content="print('hello')"),
            ProcessedFile(path="tests/test_main.py", content="def test(): pass"),
        ]

        result = build_filtered_file_tree(files)

        assert "src" in result
        assert "main.py" in result["src"]
        assert "tests" in result
        assert "test_main.py" in result["tests"]

    def test_nested_paths(self):
        """Test nested file paths"""
        files = [
            ProcessedFile(path="a/b/c/deep.py", content="# deep"),
        ]

        result = build_filtered_file_tree(files)

        assert "a" in result
        assert "b" in result["a"]
        assert "c" in result["a"]["b"]
        assert "deep.py" in result["a"]["b"]["c"]


class TestGenerateOutputWithFullStructure:
    """Test cases for generate_output with full directory structure"""

    def test_full_structure_enabled(self, tmp_path):
        """Test output generation with full directory structure enabled"""
        # Create test files
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')")
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "pkg.json").write_text("{}")

        # Build full tree
        full_tree = build_full_file_tree(tmp_path)

        # Create processed files (only main.py)
        processed_files = [
            ProcessedFile(path="src/main.py", content="print('hello')"),
        ]

        config = RepomixConfig()
        config.output.include_full_directory_structure = True
        config.output.show_directory_structure = True

        file_char_counts = {"src/main.py": 15}
        file_token_counts = {"src/main.py": 0}

        result = generate_output(
            processed_files=processed_files,
            config=config,
            file_char_counts=file_char_counts,
            file_token_counts=file_token_counts,
            file_tree=full_tree,
        )

        # Full tree should include node_modules
        assert "node_modules" in result
        assert "src" in result

    def test_full_structure_disabled(self, tmp_path):
        """Test output generation with full directory structure disabled"""
        # Create test files
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hello')")
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "pkg.json").write_text("{}")

        # Build filtered tree (would normally exclude node_modules)
        config = RepomixConfig()
        filtered_tree = build_file_tree_with_ignore(tmp_path, config)

        # Create processed files (only main.py)
        processed_files = [
            ProcessedFile(path="src/main.py", content="print('hello')"),
        ]

        config.output.include_full_directory_structure = False
        config.output.show_directory_structure = True

        file_char_counts = {"src/main.py": 15}
        file_token_counts = {"src/main.py": 0}

        result = generate_output(
            processed_files=processed_files,
            config=config,
            file_char_counts=file_char_counts,
            file_token_counts=file_token_counts,
            file_tree=filtered_tree,
        )

        # Filtered tree should NOT include node_modules
        assert "node_modules" not in result
        assert "src" in result


class TestConfigOption:
    """Test cases for include_full_directory_structure config option"""

    def test_default_value(self):
        """Test default value is False"""
        config = RepomixConfig()
        assert config.output.include_full_directory_structure is False

    def test_can_be_enabled(self):
        """Test option can be enabled"""
        config = RepomixConfig()
        config.output.include_full_directory_structure = True
        assert config.output.include_full_directory_structure is True


if __name__ == "__main__":
    pytest.main([__file__])
