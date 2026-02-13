"""
Test suite for .ignore file support and --no-dot-ignore flag (Issue #17)
"""

import tempfile
from pathlib import Path

from src.repomix.cli.cli_run import create_parser
from src.repomix.config.config_schema import RepomixConfig
from src.repomix.core.file.file_search import get_ignore_patterns


class TestDotIgnoreFlag:
    """Test cases for --no-dot-ignore CLI flag"""

    def test_parser_no_dot_ignore_flag(self):
        """Test parser recognizes --no-dot-ignore flag"""
        parser = create_parser()
        args = parser.parse_args(["--no-dot-ignore"])
        assert args.no_dot_ignore is True

    def test_parser_no_dot_ignore_default_false(self):
        """Test --no-dot-ignore defaults to False"""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.no_dot_ignore is False

    def test_config_use_dot_ignore_default_true(self):
        """Test use_dot_ignore defaults to True in config"""
        config = RepomixConfig()
        assert config.ignore.use_dot_ignore is True

    def test_config_use_dot_ignore_from_dict(self):
        """Test use_dot_ignore from dict config"""
        config = RepomixConfig(ignore={"use_dot_ignore": False})
        assert config.ignore.use_dot_ignore is False


class TestDotIgnoreFileReading:
    """Test .ignore file reading in file search"""

    def test_dot_ignore_file_patterns_included(self):
        """Test .ignore file patterns are included when use_dot_ignore is True"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .ignore file
            ignore_file = Path(tmpdir) / ".ignore"
            ignore_file.write_text("*.log\nbuild/\n")

            config = RepomixConfig()
            config.ignore.use_default_ignore = False
            config.ignore.use_gitignore = False
            config.ignore.use_dot_ignore = True

            patterns = get_ignore_patterns(tmpdir, config)
            assert "*.log" in patterns
            assert "build/" in patterns

    def test_dot_ignore_file_patterns_excluded(self):
        """Test .ignore file patterns are excluded when use_dot_ignore is False"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .ignore file
            ignore_file = Path(tmpdir) / ".ignore"
            ignore_file.write_text("*.log\nbuild/\n")

            config = RepomixConfig()
            config.ignore.use_default_ignore = False
            config.ignore.use_gitignore = False
            config.ignore.use_dot_ignore = False

            patterns = get_ignore_patterns(tmpdir, config)
            assert "*.log" not in patterns
            assert "build/" not in patterns

    def test_dot_ignore_comments_skipped(self):
        """Test comments in .ignore file are skipped"""
        with tempfile.TemporaryDirectory() as tmpdir:
            ignore_file = Path(tmpdir) / ".ignore"
            ignore_file.write_text("# This is a comment\n*.log\n# Another comment\n")

            config = RepomixConfig()
            config.ignore.use_default_ignore = False
            config.ignore.use_gitignore = False
            config.ignore.use_dot_ignore = True

            patterns = get_ignore_patterns(tmpdir, config)
            assert "*.log" in patterns
            assert "# This is a comment" not in patterns

    def test_no_dot_ignore_file_no_error(self):
        """Test no error when .ignore file doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = RepomixConfig()
            config.ignore.use_default_ignore = False
            config.ignore.use_gitignore = False
            config.ignore.use_dot_ignore = True

            patterns = get_ignore_patterns(tmpdir, config)
            # Should not raise, just return empty (or only repomixignore patterns)
            assert isinstance(patterns, list)
