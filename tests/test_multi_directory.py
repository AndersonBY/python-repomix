"""
Test suite for multiple directories support (Issue #20)
"""

import os
import tempfile
import pytest
from unittest.mock import patch, Mock

from src.repomix.cli.cli_run import create_parser
from src.repomix.cli.actions.default_action import run_default_action
from src.repomix.core.repo_processor import RepoProcessor
from src.repomix.config.config_schema import RepomixConfig
from src.repomix.shared.error_handle import RepomixError


class TestMultiDirectoryParser:
    """Test CLI parser for multiple directories"""

    def test_no_directories_defaults_to_dot(self):
        parser = create_parser()
        args = parser.parse_args([])
        assert args.directories == ["."]

    def test_single_directory(self):
        parser = create_parser()
        args = parser.parse_args(["src"])
        assert args.directories == ["src"]

    def test_multiple_directories(self):
        parser = create_parser()
        args = parser.parse_args(["src", "lib", "tests"])
        assert args.directories == ["src", "lib", "tests"]

    def test_multiple_directories_with_options(self):
        parser = create_parser()
        args = parser.parse_args(["src", "lib", "--verbose", "--output", "out.md"])
        assert args.directories == ["src", "lib"]
        assert args.verbose is True
        assert args.output == "out.md"


class TestRepoProcessorMultiDir:
    """Test RepoProcessor with multiple directories"""

    def test_init_with_single_directory(self):
        """Single directory should work as before"""
        config = RepomixConfig()
        processor = RepoProcessor(directory=".", config=config)
        assert processor.directories == ["."]
        assert processor.directory == "."

    def test_init_with_directories_list(self):
        """Multiple directories should be stored"""
        config = RepomixConfig()
        processor = RepoProcessor(directories=["src", "lib"], config=config)
        assert processor.directories == ["src", "lib"]
        assert processor.directory == "src"

    def test_init_requires_directory_or_repo_url(self):
        """Should raise if no directory or repo_url provided"""
        with pytest.raises(RepomixError):
            RepoProcessor(config=RepomixConfig())


class TestMultiDirectoryProcessing:
    """Test actual multi-directory processing"""

    def _create_temp_dirs(self):
        """Create two temp directories with files for testing."""
        base = tempfile.mkdtemp()
        dir_a = os.path.join(base, "project_a")
        dir_b = os.path.join(base, "project_b")
        os.makedirs(dir_a)
        os.makedirs(dir_b)

        # Create files in dir_a
        with open(os.path.join(dir_a, "main.py"), "w") as f:
            f.write("print('hello from project_a')\n")
        with open(os.path.join(dir_a, "utils.py"), "w") as f:
            f.write("def helper(): pass\n")

        # Create files in dir_b
        with open(os.path.join(dir_b, "app.js"), "w") as f:
            f.write("console.log('hello from project_b');\n")

        return base, dir_a, dir_b

    def test_multi_dir_processes_all_files(self):
        """Multi-directory processing should include files from all directories"""
        base, dir_a, dir_b = self._create_temp_dirs()
        try:
            config = RepomixConfig()
            config.output.calculate_tokens = False
            config.security.enable_security_check = False
            processor = RepoProcessor(directories=[dir_a, dir_b], config=config)
            result = processor.process(write_output=False)

            # Should have files from both directories
            assert result.total_files >= 3  # main.py, utils.py, app.js

            # File paths should be prefixed with root labels
            file_paths = list(result.file_char_counts.keys())
            has_project_a = any("project_a" in p for p in file_paths)
            has_project_b = any("project_b" in p for p in file_paths)
            assert has_project_a, f"Expected project_a files in {file_paths}"
            assert has_project_b, f"Expected project_b files in {file_paths}"
        finally:
            import shutil
            shutil.rmtree(base)

    def test_multi_dir_tree_has_root_labels(self):
        """Multi-directory tree should have root labels as top-level keys"""
        base, dir_a, dir_b = self._create_temp_dirs()
        try:
            config = RepomixConfig()
            config.output.calculate_tokens = False
            config.security.enable_security_check = False
            processor = RepoProcessor(directories=[dir_a, dir_b], config=config)
            result = processor.process(write_output=False)

            # Tree should have root labels as top-level keys
            assert "project_a" in result.file_tree
            assert "project_b" in result.file_tree
        finally:
            import shutil
            shutil.rmtree(base)

    def test_single_dir_no_root_label(self):
        """Single directory should not have root label prefix"""
        base, dir_a, _ = self._create_temp_dirs()
        try:
            config = RepomixConfig()
            config.output.calculate_tokens = False
            config.security.enable_security_check = False
            processor = RepoProcessor(directories=[dir_a], config=config)
            result = processor.process(write_output=False)

            # File paths should NOT be prefixed with root label
            file_paths = list(result.file_char_counts.keys())
            assert any("main.py" in p for p in file_paths)
            # Should not have "project_a/" prefix for single dir
            assert not any(p.startswith("project_a/") for p in file_paths)
        finally:
            import shutil
            shutil.rmtree(base)


class TestRunDefaultActionMultiDir:
    """Test run_default_action with multiple directories"""

    def test_accepts_list(self):
        """run_default_action should accept a list of directories"""
        with patch("src.repomix.cli.actions.default_action.load_config") as mock_config, \
             patch("src.repomix.cli.actions.default_action.RepoProcessor") as mock_proc, \
             patch("src.repomix.cli.actions.default_action._print_results"):
            mock_config.return_value = RepomixConfig()
            mock_result = Mock()
            mock_proc.return_value.process.return_value = mock_result
            mock_result.pack_result = Mock()

            run_default_action(["src", "lib"], ".", {})
            mock_proc.assert_called_once()
            call_kwargs = mock_proc.call_args[1]
            assert call_kwargs["directories"] == ["src", "lib"]

    def test_accepts_single_string_backward_compat(self):
        """run_default_action should accept a single string for backward compatibility"""
        with patch("src.repomix.cli.actions.default_action.load_config") as mock_config, \
             patch("src.repomix.cli.actions.default_action.RepoProcessor") as mock_proc, \
             patch("src.repomix.cli.actions.default_action._print_results"):
            mock_config.return_value = RepomixConfig()
            mock_result = Mock()
            mock_proc.return_value.process.return_value = mock_result
            mock_result.pack_result = Mock()

            run_default_action(".", ".", {})
            mock_proc.assert_called_once()
            call_kwargs = mock_proc.call_args[1]
            assert call_kwargs["directories"] == ["."]

    def test_stdin_rejects_multiple_directories(self):
        """--stdin should reject multiple directories"""
        with pytest.raises(RepomixError, match="do not specify directory arguments"):
            run_default_action(["src", "lib"], ".", {"stdin": True})
